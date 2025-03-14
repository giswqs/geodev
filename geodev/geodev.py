"""Main module."""

import ipyleaflet


class Map(ipyleaflet.Map):
    def __init__(self, center=[20, 0], zoom=2, height="600px", **kwargs):
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height

    def add_basemap(self, basemap="OpenTopoMap"):

        url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        layer = ipyleaflet.TileLayer(url=url, name=basemap)
        self.add(layer)

    def add_google_map(self, map_type="ROADMAP"):

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
