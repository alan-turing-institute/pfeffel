import json
from unittest import TestCase

from src.clean_data import load_clean_data
from src.trip import Trip


class TestTrip(TestCase):
    def setUp(self):
        self.data = load_clean_data("data/")
        with open("data/stations_loc.json") as f:
            self.stations = json.load(f)

        self.trip = Trip(self.data, 15305469, self.stations)


class TestTripOther:
    def test_init(self):
        data = load_clean_data("data/")

        trip = Trip(data, 15305469)
        self.assertEqual(trip.bike, 6270)
