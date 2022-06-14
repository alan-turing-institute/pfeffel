import json
from unittest import TestCase

import folium

from src.clean_data import load_clean_data
from src.trip import Trip


class TestTrip(TestCase):
    def setUp(self):
        self.data = load_clean_data("data/")
        with open("data/stations_loc.json") as f:
            self.stations = json.load(f)

        self.trip = Trip(self.data, 60852662, self.stations)
        self.key = "f339aa90aba2b309"
        self.trip.get_route(self.key)

    def test_trip(self):
        self.assertEqual(self.trip.bike, 10746)

    def test_route(self):

        self.assertEqual(self.trip.route["time"], "703")

    def test_routes(self):

        for route in self.data.index[:10]:

            trip = Trip(self.data, route, self.stations)
            trip.get_route(self.key)

            # Create base map
            London = [51.506949, -0.122876]
            map = folium.Map(
                location=London, zoom_start=12, tiles="CartoDB positron"
            )

            trip.folium_route().add_to(map)

        f = "map_multiiple_trips.html"
        map.save(f)

    def test_map(self):

        map = self.trip.map()

        f = "map_trip.html"
        map.save(f)
