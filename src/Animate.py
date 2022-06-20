import json
import pickle
import pathlib

import cartopy.crs as ccrs
import numpy as np
import pandas as pd
from cartopy.io.img_tiles import OSM
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

DATA_DIR = "../data"
DATA_FILE = pathlib.Path(DATA_DIR, "latest_cleaned_data_sample.pickle")
STATION_NAMES_FILE = pathlib.Path(DATA_DIR, "latest_station_names.pickle")
STATION_COORDS_FILE = pathlib.Path(DATA_DIR, "stations_loc.json")


df = pd.read_pickle(DATA_FILE)
with open(STATION_NAMES_FILE, "rb") as f:
    station_allnames = pickle.load(f)

with open(STATION_COORDS_FILE, "r") as f:
    station_latlon = json.load(f)


start_time = np.datetime64("2016-10-07T00:00:00")

pos = np.array([[v["lon"], v["lat"]] for k, v in station_latlon.items()])

imagery = OSM(desired_tile_form="L")
fig, ax = plt.subplots(
    1, 1, figsize=(10, 10), subplot_kw=dict(projection=imagery.crs)
)
ax.set_extent((-0.24, 0.02, 51.45, 51.56))
ax.add_image(imagery, 14, cmap="gray")

xynps = ax.projection.transform_points(
    ccrs.Geodetic(),
    pos[:,0], pos[:,1],
)

ax.scatter(xynps[:,0], xynps[:,1], s=3., c="C1")

xynps = ax.projection.transform_points(ccrs.Geodetic(), np.array(-0.0886), np.array(51.451647))

lns = [ax.text(xynps[0,0], xynps[0,1], str(start_time), fontsize=20)]

nlines = 5000

for i in range(nlines):
    ln, = ax.plot([], [], color="C0", alpha=0.5)
    lns.append(ln)

def init():
    return lns

def update(frame):
    t = start_time + np.timedelta64(frame*60*10, "s")
    tmp = df[df["start_date"] <= t]
    tmp = tmp[tmp["end_date"] >= t]
    for k, ln in enumerate(lns):
        if k == 0:
            ln.set_text(str(t))
        else:
            ln.set_data([], [])
    for k, vals in enumerate(zip(tmp["start_station_id"], tmp["end_station_id"])):
        start, end = vals
        if k >= nlines:
            print("exceeded length")
            break
        try:
            xynps = ax.projection.transform_points(
                ccrs.Geodetic(),
                np.array([station_latlon[str(start)]["lon"], station_latlon[str(end)]["lon"]]),
                np.array([station_latlon[str(start)]["lat"], station_latlon[str(end)]["lat"]]),
            )
            lns[k + 1].set_data(xynps[:,0], xynps[:,1])
        except KeyError:
            lns[k + 1].set_data([], [])
    return lns

ani = FuncAnimation(fig, update, frames=np.arange(0, 2*6*24, 1),
                    blit=True)
ani.save("animation.gif", fps=4)
