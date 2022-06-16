import folium

from trip import Trip
from utils import get_colours


class Bike:
    def __init__(self, id):
        self.id = id

    def get_trips(self, df, stations):

        routes = [Trip(df, self.id, trip_id, stations) for trip_id in df.index]
        return routes

    def get_chains(self, stations):
        chain_ids = self.bike_rides.chain_id.to_list()
        chains = {}
        for chain_id in chain_ids:
            chain_rides = self.bike_rides[
                self.bike_rides["chain_id"] == chain_id
            ]
            chains[chain_id] = self.get_trips(chain_rides, stations)
        self.chains = chains

    def get_story(self, dataset, stations):
        bike_rides = dataset[dataset["bike_id"] == self.id]
        self.bike_rides = bike_rides
        self.get_chains(stations)

    def get_usage(self):
        usage = self.bike_rides["duration"].sum()
        return usage

    def visualize_routes(self, key):

        colours = ["red"]

        # Create base map
        London = [51.506949, -0.122876]
        map = folium.Map(
            location=London, zoom_start=12, tiles="CartoDB positron"
        )
        for chain_id, chain in self.chains.items():
            colours = get_colours(len(chain))
            for counter, trip in enumerate(chain):
                trip.get_route(key)
                if trip.route == {}:
                    continue

                trip.folium_route(key, colours[counter]).add_to(map)

            f = "output/" + str(self.id) + "_" + str(chain_id) + ".html"
            map.save(f)
