import json

import pandas as pd

import bike

with open("../data/stations_loc.json") as f:
    stations = json.load(f)

data = pd.read_pickle("../data/cleaned_data_20220612_1302_sample.pickle")

bike_ids = set(data["bike_id"])

bike = bike.Bike(id=8710)
bike.get_story(data)
bike.get_routes(stations)
bike.visualize_routes()
# clean_data.clean_station_json("../test/data/bike_stations_dump.json")
