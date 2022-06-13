from src.clean_data import load_clean_data
from src.trip import Trip

class TestTrip:
    def test_init(self):
        data = load_clean_data('data/')

        trip = Trip(data, 15305469)
        self.assertEqual(trip.bike, 6270)


