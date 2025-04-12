"""Main module."""

import os
import ipyleaflet
import ipywidgets as widgets


class Map(ipyleaflet.Map):
    def __init__(self, center=[20, 0], zoom=2, height="600px", **kwargs):

        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height
        self.scroll_wheel_zoom = True

    def add_basemap(self, basemap="OpenTopoMap"):
        """Add basemap to the map.

        Args:
            basemap (str, optional): Basemap name. Defaults to "OpenTopoMap".
        """

        url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        layer = ipyleaflet.TileLayer(url=url, name=basemap)
        self.add(layer)

    def add_basemap_gui(self, options=None, position="topright"):
        """Adds a graphical user interface (GUI) for selecting basemaps.

        Args:
            options (list, optional): A list of basemap options to display in the dropdown.
                Defaults to ["OpenStreetMap.Mapnik", "OpenTopoMap", "Esri.WorldImagery", "CartoDB.DarkMatter"].
            position (str, optional): The position of the widget on the map. Defaults to "topright".

        Behavior:
            - A toggle button is used to show or hide the dropdown and close button.
            - The dropdown allows users to select a basemap from the provided options.
            - The close button removes the widget from the map.

        Event Handlers:
            - `on_toggle_change`: Toggles the visibility of the dropdown and close button.
            - `on_button_click`: Closes and removes the widget from the map.
            - `on_dropdown_change`: Updates the map's basemap when a new option is selected.
        """
        if options is None:
            options = [
                "OpenStreetMap.Mapnik",
                "OpenTopoMap",
                "Esri.WorldImagery",
                "CartoDB.DarkMatter",
            ]

        toggle = widgets.ToggleButton(
            value=True,
            button_style="",
            tooltip="Click me",
            icon="map",
        )
        toggle.layout = widgets.Layout(width="38px", height="38px")

        dropdown = widgets.Dropdown(
            options=options,
            value=options[0],
            description="Basemap:",
            style={"description_width": "initial"},
        )
        dropdown.layout = widgets.Layout(width="250px", height="38px")

        button = widgets.Button(
            icon="times",
        )
        button.layout = widgets.Layout(width="38px", height="38px")

        hbox = widgets.HBox([toggle, dropdown, button])

        def on_toggle_change(change):
            if change["new"]:
                hbox.children = [toggle, dropdown, button]
            else:
                hbox.children = [toggle]

        toggle.observe(on_toggle_change, names="value")

        def on_button_click(b):
            hbox.close()
            toggle.close()
            dropdown.close()
            button.close()

        button.on_click(on_button_click)

        def on_dropdown_change(change):
            if change["new"]:
                self.layers = self.layers[:-2]
                self.add_basemap(change["new"])

        dropdown.observe(on_dropdown_change, names="value")

        control = ipyleaflet.WidgetControl(widget=hbox, position=position)
        self.add(control)

    def add_widget(self, widget, position="topright", **kwargs):
        """Add a widget to the map.

        Args:
            widget (ipywidgets.Widget): The widget to add.
            position (str, optional): Position of the widget. Defaults to "topright".
            **kwargs: Additional keyword arguments for the WidgetControl.
        """
        control = ipyleaflet.WidgetControl(widget=widget, position=position, **kwargs)
        self.add(control)

    def add_google_map(self, map_type="ROADMAP"):
        """Add Google Map to the map.

        Args:
            map_type (str, optional): Map type. Defaults to "ROADMAP".
        """
        map_types = {
            "ROADMAP": "m",
            "SATELLITE": "s",
            "HYBRID": "y",
            "TERRAIN": "p",
        }
        map_type = map_types[map_type.upper()]

        url = (
            f"https://mt1.google.com/vt/lyrs={map_type.lower()}&x={{x}}&y={{y}}&z={{z}}"
        )
        layer = ipyleaflet.TileLayer(url=url, name="Google Map")
        self.add(layer)

    def add_geojson(
        self,
        data,
        zoom_to_layer=True,
        hover_style=None,
        **kwargs,
    ):
        """Adds a GeoJSON layer to the map.

        Args:
            data (str or dict): The GeoJSON data. Can be a file path (str) or a dictionary.
            zoom_to_layer (bool, optional): Whether to zoom to the layer's bounds. Defaults to True.
            hover_style (dict, optional): Style to apply when hovering over features. Defaults to {"color": "yellow", "fillOpacity": 0.2}.
            **kwargs: Additional keyword arguments for the ipyleaflet.GeoJSON layer.

        Raises:
            ValueError: If the data type is invalid.
        """
        import geopandas as gpd

        if hover_style is None:
            hover_style = {"color": "yellow", "fillOpacity": 0.2}

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__
        elif isinstance(data, dict):
            geojson = data
        layer = ipyleaflet.GeoJSON(data=geojson, hover_style=hover_style, **kwargs)
        self.add_layer(layer)

        if zoom_to_layer:
            bounds = gdf.total_bounds
            self.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    def add_shp(self, data, **kwargs):
        """Adds a shapefile to the map.

        Args:
            data (str): The file path to the shapefile.
            **kwargs: Additional keyword arguments for the GeoJSON layer.
        """
        import geopandas as gpd

        gdf = gpd.read_file(data)
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_gdf(self, gdf, **kwargs):
        """Adds a GeoDataFrame to the map.

        Args:
            gdf (geopandas.GeoDataFrame): The GeoDataFrame to add.
            **kwargs: Additional keyword arguments for the GeoJSON layer.
        """
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_vector(self, data, **kwargs):
        """Adds vector data to the map.

        Args:
            data (str, geopandas.GeoDataFrame, or dict): The vector data. Can be a file path, GeoDataFrame, or GeoJSON dictionary.
            **kwargs: Additional keyword arguments for the GeoJSON layer.

        Raises:
            ValueError: If the data type is invalid.
        """
        import geopandas as gpd

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            self.add_gdf(gdf, **kwargs)
        elif isinstance(data, gpd.GeoDataFrame):
            self.add_gdf(data, **kwargs)
        elif isinstance(data, dict):
            self.add_geojson(data, **kwargs)
        else:
            raise ValueError("Invalid data type")

    def add_layer_control(self):
        """Adds a layer control widget to the map."""
        control = ipyleaflet.LayersControl(position="topright")
        self.add_control(control)

    def add_raster(self, filepath, **kwargs):

        from localtileserver import TileClient, get_leaflet_tile_layer

        client = TileClient(filepath)
        tile_layer = get_leaflet_tile_layer(client, **kwargs)

        self.add(tile_layer)
        self.center = client.center()
        self.zoom = client.default_zoom

    def add_image(self, image, bounds=None, **kwargs):
        """Adds an image to the map.

        Args:
            image (str): The file path to the image.
            bounds (list, optional): The bounds for the image. Defaults to None.
            **kwargs: Additional keyword arguments for the ipyleaflet.ImageOverlay layer.
        """

        if bounds is None:
            bounds = [[-90, -180], [90, 180]]
        overlay = ipyleaflet.ImageOverlay(url=image, bounds=bounds, **kwargs)
        self.add(overlay)

    def add_video(self, video, bounds=None, **kwargs):
        """Adds a video to the map.

        Args:
            video (str): The file path to the video.
            bounds (list, optional): The bounds for the video. Defaults to None.
            **kwargs: Additional keyword arguments for the ipyleaflet.VideoOverlay layer.
        """

        if bounds is None:
            bounds = [[-90, -180], [90, 180]]
        overlay = ipyleaflet.VideoOverlay(url=video, bounds=bounds, **kwargs)
        self.add(overlay)

    def add_wms_layer(
        self, url, layers, format="image/png", transparent=True, **kwargs
    ):
        """Adds a WMS layer to the map.

        Args:
            url (str): The WMS service URL.
            layers (str): The layers to display.
            **kwargs: Additional keyword arguments for the ipyleaflet.WMSLayer layer.
        """
        layer = ipyleaflet.WMSLayer(
            url=url, layers=layers, format=format, transparent=transparent, **kwargs
        )
        self.add(layer)
