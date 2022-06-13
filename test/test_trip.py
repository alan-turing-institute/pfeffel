import json

from src.clean_data import load_clean_data
from src.trip import Trip
from unittest import TestCase
import json

class TestTrip(TestCase):

    def setUp(self):
        self.data =  load_clean_data('data/')
        with open('data/stations_loc.json') as f:
            self.stations = json.load(f)

        self.trip = Trip(self.data, 15305469,self.stations)

    def test_init(self):
        self.assertEqual(self.trip.bike, 6270)

    #def test_get_route(self):

     #   self.trip.get_route()


