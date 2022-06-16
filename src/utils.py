import json
import os
from datetime import datetime, timedelta

import movingpandas as mpd
import pandas as pd
import seaborn as sns
from geopandas import GeoDataFrame
from shapely.geometry import Point


def get_colours(steps):
    colours = sns.color_palette("mako").as_hex()
    rev_colours = sns.color_palette("mako").as_hex()
    rev_colours.reverse()
    colours = rev_colours + colours
    while len(colours) < steps:
        colours += colours
    return colours


def traj_to_timestamped_geojson(trajectory):
    features = []
    df = trajectory.df.copy()
    df["previous_geometry"] = df["geometry"].shift()
    df["time"] = df.index
    df["previous_time"] = df["time"].shift()
    for _, row in df.iloc[1:].iterrows():
        coordinates = [
            [
                row["previous_geometry"].xy[0][0],
                row["previous_geometry"].xy[1][0],
            ],
            [row["geometry"].xy[0][0], row["geometry"].xy[1][0]],
        ]
        times = [row["previous_time"].isoformat(), row["time"].isoformat()]
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates,
                },
                "properties": {
                    "times": times,
                    "style": {
                        "color": row["colour"],
                        "weight": 5,
                    },
                },
            }
        )
    return features


def get_trajectory(bike_id):

    route_folder = "output/routes/"
    chains = [
        filename
        for filename in os.listdir(route_folder)
        if str(bike_id) + "_" in filename
    ]

    times = []
    geometry = []
    colours = []

    many_colurs = get_colours(len(chains))

    for c in range(len(chains)):
        chain = chains[c]
        with open(route_folder + chain) as f:
            d = json.load(f)
        if len(d) > 0:
            geometry += [
                Point([float(y) for y in x.split(",")])
                for x in d["coordinates"].split(" ")
            ]
            if len(times) == 0:
                time_now = datetime.now()
            else:
                time_now = times[-1]
            times += [
                time_now + timedelta(seconds=10 * t + 1)
                for t in range(len(d["coordinates"].split(" ")))
            ]
            colours += [
                many_colurs[c] for x in range(len(d["coordinates"].split(" ")))
            ]

    df = pd.DataFrame()

    df["t"] = times
    df["trajectory_id"] = [1 for x in range(len(geometry))]
    df["sequence"] = [x + 1 for x in range(len(geometry))]
    df["colour"] = colours

    gdf = GeoDataFrame(df, crs="EPSG:4326", geometry=geometry)
    gdf = gdf.set_index("t")

    trajs = mpd.TrajectoryCollection(gdf, "trajectory_id")
    trajs = mpd.MinTimeDeltaGeneralizer(trajs).generalize(
        tolerance=timedelta(seconds=1)
    )
    traj = trajs.trajectories[0]
    return traj
