import requests as requests


class Trip:
    def __init__(self, data, trip_id, station_data):
        df = data[data.index == trip_id]

        self.init_station = {
            "name": df.start_station_name.values[0],
            "id": df.start_station_id.values[0],
            "latitude": station_data[df.start_station_name.values[0]]["lat"],
            "longitude": station_data[df.start_station_name.values[0]]["lon"],
        }
        self.end_station = {
            "name": df.end_station_name.values[0],
            "id": df.end_station_id.values[0],
            "latitude": station_data[df.end_station_name.values[0]]["lat"],
            "longitude": station_data[df.end_station_name.values[0]]["lon"],
        }
        self.bike = df.bike_id.values[0]
        self.duration = df.duration.values[0]
        self.date = {
            "start": df.start_date.values[0],
            "end": df.end_date.values[0],
        }
        self.circular = self.init_station == self.end_station

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
