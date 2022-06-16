import json

import pandas as pd

from bike import Bike
from src import utils

with open("data/stations_loc.json") as f:
    stations = json.load(f)

key = open("data/cycle_street_key.txt", "r").read()

data = pd.read_pickle("data/top_ten_bikes.pickle")


def check_id(row, stations):
    start_id = str(int(row["start_station_id"]))
    end_id = str(int(row["end_station_id"]))
    if str(start_id) in stations.keys() and str(end_id) in stations.keys():
        return True
    return False


data["check_stations_ids"] = data.apply(
    lambda row: check_id(row, stations), axis=1
)
data = data[data["check_stations_ids"] is True]
data = data[:100]
bike_id = 893

bike = Bike(id=bike_id)
bike.get_story(data, stations)
bike.visualize_routes(key)
traj = utils.get_trajectory(bike_id)
