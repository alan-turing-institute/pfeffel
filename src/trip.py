import folium
import requests as requests


class Trip:
    def __init__(self, data, trip_id, station_data):
        df = data[data.index == trip_id]

        self.init_station = {
            "name": df.start_station_name.values[0],
            "id": df.start_station_id.values[0],
            "latitude": station_data[str(int(df.start_station_id.values[0]))][
                "lat"
            ],
            "longitude": station_data[str(int(df.start_station_id.values[0]))][
                "lon"
            ],
        }
        self.end_station = {
            "name": df.end_station_name.values[0],
            "id": df.end_station_id.values[0],
            "latitude": station_data[str(int(df.end_station_id.values[0]))][
                "lat"
            ],
            "longitude": station_data[str(int(df.end_station_id.values[0]))][
                "lon"
            ],
        }
        self.bike = df.bike_id.values[0]
        self.duration = df.duration.values[0]
        self.date = {
            "start": df.start_date.values[0],
            "end": df.end_date.values[0],
        }
        self.circular = self.init_station == self.end_station
        self.route = {}

    def get_route(self, key):

        if self.circular:
            print("This is a circular trip, no route avalaible.")
            self.route = {}
        else:
            plans = ["balanced", "fastest", "quietest", "shortest"]

            closest_time = 10000
            trip_data = {}

            for plan in plans:
                name = (
                    "https://www.cyclestreets.net/api/journey.json?key="
                    + key
                    + "&itinerarypoints="
                    + str(self.init_station["longitude"])
                    + ","
                    + str(self.init_station["latitude"])
                    + "|"
                    + str(self.end_station["longitude"])
                    + ","
                    + str(self.end_station["latitude"])
                    + "&plan="
                    + plan
                )
                data = requests.get(name).json()["marker"][0]["@attributes"]
                time = int(data["time"])

                if abs(self.duration - time) < closest_time:
                    closest_time = abs(time - self.duration)
                    trip_data = data

            self.route = trip_data

    def map(self):

        # Create base map
        London = [51.506949, -0.122876]
        map = folium.Map(
            location=London, zoom_start=12, tiles="CartoDB positron"
        )

        self.folium_route().add_to(map)

        return map

    def folium_route(self, colour="red"):

        if self.route == {}:
            self.get_route()

        coords = [
            (float(i.split(",")[1]), float(i.split(",")[0]))
            for i in self.route["coordinates"].split(" ")
        ]

        folium_route = folium.PolyLine(
            coords, color=colour, weight=10, opacity=0.8
        )

        return folium_route
