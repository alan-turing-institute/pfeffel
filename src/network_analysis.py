import json
import pickle
import re

import cartopy.crs as ccrs
import community
import networkx as nx
import numpy as np
import pandas as pd
from cartopy.io.img_tiles import OSM
from matplotlib import pyplot as plt

DATA_FILE = "latest_cleaned_data_samples.pickle"
STATION_NAMES_FILE = "latest_station_names.pickle"
STATION_COORDS_FILE = "../data/stations_loc.json"
TRIP_COUNT_THRESHOLD = 2e-5
NUM_LABELS = 16
FONT_SIZE = 10
EDGE_WIDTH_FACTOR = 1e-2
NODE_SIZE_FACTOR = 0.03
MIN_EDGE_ALPHA = 0.1
MAX_EDGE_ALPHA = 0.9

df = pd.read_pickle(DATA_FILE)
with open(STATION_NAMES_FILE, "rb") as f:
    station_allnames = pickle.load(f)

with open(STATION_COORDS_FILE, "r") as f:
    station_latlon = json.load(f)


def get_station_name(id):
    name = sorted(station_allnames[id])[0]
    name = re.split(";|,|:", name)[0]
    return name


trip_counts = (
    (
        df[["start_station_id", "end_station_id", "bike_id"]]
        .groupby(["start_station_id", "end_station_id"])
        .count()
    )
    .reset_index()
    .rename(columns={"bike_id": "trip_count"})
)
trip_counts = trip_counts.sort_values("trip_count")
total_num_trips = trip_counts["trip_count"].sum()
print(trip_counts)
print(total_num_trips)
trip_counts = trip_counts[
    trip_counts["trip_count"] >= TRIP_COUNT_THRESHOLD * total_num_trips
]
print(trip_counts)


graph = nx.from_pandas_edgelist(
    trip_counts,
    source="start_station_id",
    target="end_station_id",
    edge_attr="trip_count",
    create_using=nx.DiGraph,
)
# Drop self-loops
graph.remove_edges_from(nx.selfloop_edges(graph))

nodes = graph.nodes()
pos = {int(k): (v["lon"], v["lat"]) for k, v in station_latlon.items()}
weights = np.array(
    [graph.edges[e]["trip_count"] * EDGE_WIDTH_FACTOR for e in graph.edges]
)
station_sizes = (
    trip_counts[["start_station_id", "trip_count"]]
    .groupby(["start_station_id"])
    .sum()
    .sort_values("trip_count", ascending=False)
)
labels = {k: get_station_name(k) for k in station_sizes.index[:NUM_LABELS]}

imagery = OSM()
fig, ax = plt.subplots(
    1, 1, figsize=(10, 10), subplot_kw=dict(projection=imagery.crs)
)
ax.set_extent((-0.24, 0.02, 51.45, 51.56))
ax.add_image(imagery, 14)
xynps = ax.projection.transform_points(
    ccrs.Geodetic(),
    np.array([p[0] for p in pos.values()]),
    np.array([p[1] for p in pos.values()]),
)
pos = {k: (xynps[i, 0], xynps[i, 1]) for i, k in enumerate(pos.keys())}

# Communitities
graph_undirected = graph.to_undirected()
# print(graph.edges[(279, 512)])
print(graph.edges[(512, 279)])
print(graph_undirected.edges[(279, 512)])
partition = community.best_partition(graph_undirected, weight="trip_count")
df_partition = pd.DataFrame(partition, index=[0]).T
print(df_partition.value_counts())
print(set(partition.values()))
quit()

# Plots
nx.draw_networkx_nodes(
    G=graph,
    pos=pos,
    nodelist=station_sizes.index,
    node_color="#148381",
    alpha=1.0,
    node_size=station_sizes["trip_count"] * NODE_SIZE_FACTOR,
    ax=ax,
)
max_weight = np.max(weights)
min_weight = np.min(weights)
alpha_mult_coeff = (MAX_EDGE_ALPHA - MIN_EDGE_ALPHA) / (
    max_weight - min_weight
)
alpha_add_coeff = (
    max_weight * MIN_EDGE_ALPHA - min_weight * MAX_EDGE_ALPHA
) / (max_weight - min_weight)
alpha = alpha_mult_coeff * weights + alpha_add_coeff
nx.draw_networkx_edges(
    G=graph,
    pos=pos,
    edge_color="#0114EE",
    width=weights,
    alpha=alpha,
    arrows=False,
    ax=ax,
)
nx.draw_networkx_labels(
    graph,
    pos=pos,
    labels=labels,
    font_size=FONT_SIZE,
    ax=ax,
)
plt.show()
