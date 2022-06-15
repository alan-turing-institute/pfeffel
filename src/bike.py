import folium

from trip import Trip
from utils import get_colours


class Bike:
    def __init__(self, id):
        self.id = id

    def get_story(self, dataset):
        bike_rides = dataset[dataset["bike_id"] == self.id]
        self.bike_rides = bike_rides

    def get_usage(self):
        usage = self.bike_rides["duration"].sum()
        return usage

    def get_trips(self, stations):

        routes = [
            Trip(self.bike_rides, self.id, trip_id, stations)
            for trip_id in self.bike_rides.index
        ]
        self.routes = routes

    def visualize_routes(self, key):

        colours = ["red"]

        # Create base map
        London = [51.506949, -0.122876]
        map = folium.Map(
            location=London, zoom_start=12, tiles="CartoDB positron"
        )
        colours = get_colours(len(self.routes))
        for counter, trip in enumerate(self.routes):

            trip.get_route(key)
            if trip.route == {}:
                continue

            trip.folium_route(key, colours[counter]).add_to(map)

        f = "../output/" + str(self.id) + "_map_multiple_trips.html"
        map.save(f)
