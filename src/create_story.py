import json

import pandas as pd

from bike import Bike

with open("../data/stations_loc.json") as f:
    stations = json.load(f)

key = open("../data/cycle_street_key.txt", "r").read()

data = pd.read_pickle("../data/sample.pickle")

bike_ids = set(data["bike_id"])
bike = Bike(id=5735)
bike.get_story(data)
print(bike.chains)
exit()
bike.get_trips(stations)
bike.visualize_routes(key)
