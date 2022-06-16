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

STATION_NAMES_FILE = "../data/station_names_20220615_1137.pickle"
STATION_COORDS_FILE = "../data/stations_loc.json"

TRIP_COUNT_THRESHOLD = 2e-5
MAP_BOUNDARIES = (-0.223, 0.005, 51.46, 51.555)
FONT_SIZE = 10
EDGE_WIDTH_FACTOR = 1e-2
MAX_NODE_SIZE = 250.0
MIN_NODE_SIZE = 0.1
MIN_EDGE_ALPHA = 0.1
MAX_EDGE_ALPHA = 0.9
EDGE_COLOUR = "#222222"
LABEL_STATIONS = [
    # "Belgrove Street",
    # "Waterloo Station 3",
    # "Hyde Park Corner",
    # "Aquatic Centre",
    # "Bethnal Green Road",
    # "Natural History Museum",
    # "Kennington Oval",
    # "Mudchute DLR",
]


def get_station_name(id):
    with open(STATION_NAMES_FILE, "rb") as f:
        station_allnames = pickle.load(f)

    name = sorted(station_allnames[id])[0]
    name = re.split(";|,|:", name)[0].strip()
    return name


def create_network_from_data(df, trip_count_threshold):
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

    trip_counts = trip_counts[
        trip_counts["trip_count"] >= trip_count_threshold * total_num_trips
    ]

    graph = nx.from_pandas_edgelist(
        trip_counts,
        source="start_station_id",
        target="end_station_id",
        edge_attr="trip_count",
        create_using=nx.DiGraph,
    )

    return graph


def get_node_info(graph):
    with open(STATION_COORDS_FILE, "r") as f:
        station_latlon = json.load(f)

    nodes = graph.nodes()

    pos = [station_latlon[str(int(node))] for node in nodes]
    pos = [(p["lon"], p["lat"]) for p in pos]

    station_sizes = [i[1] for i in list(graph.out_degree(weight="trip_count"))]

    labels = [get_station_name(int(node)) for node in nodes]

    nodes_df = pd.DataFrame(
        {"id": list(nodes), "pos": pos, "size": station_sizes, "name": labels}
    )

    return nodes_df


def network_community_detection(graph, edge_weight):
    graph_undirected = nx.Graph()
    undirected_edges = set(sorted(graph.edges))
    for edge in undirected_edges:
        reverse_edge = (edge[1], edge[0])
        trip_count = graph.edges[edge][edge_weight]
        if reverse_edge in graph.edges:
            trip_count += graph.edges[reverse_edge][edge_weight]
        graph_undirected.add_edge(edge[0], edge[1], trip_count=trip_count)

    partition = community.best_partition(graph_undirected, weight=edge_weight)
    df_partition = pd.DataFrame(partition, index=[0]).T.reset_index()
    df_partition.columns = ["id", "partition"]

    return df_partition


def visualise_network_map(network, node_info_df):
    pass


def _scale_range(values, min_scaled, max_scaled):
    values = np.array(values)
    if min_scaled is not None:
        max_value = np.max(values)
        min_value = np.min(values)
        mult_coeff = (max_scaled - min_scaled) / (max_value - min_value)
        add_coeff = (max_value * min_scaled - min_value * max_scaled) / (
            max_value - min_value
        )
        scaled = mult_coeff * values + add_coeff
    else:
        max_value = np.max(values)
        scaled = max_scaled * values / max_value
    return scaled


def create_network_and_map(df):
    community_graph = create_network_from_data(df, TRIP_COUNT_THRESHOLD)
    nodes_info = get_node_info(community_graph)
    visualisation_graph = community_graph.copy()
    visualisation_graph.remove_edges_from(nx.selfloop_edges(community_graph))
    community_df = network_community_detection(community_graph, "trip_count")
    nodes_info = nodes_info.merge(community_df, on="id")
    nodes_info = nodes_info.sort_values(by="size", ascending=False)
    del community_df

    weights = np.array(
        [
            visualisation_graph.edges[e]["trip_count"] * EDGE_WIDTH_FACTOR
            for e in visualisation_graph.edges
        ]
    )
    labels = {
        id: name
        for id, name in zip(nodes_info["id"], nodes_info["name"])
        if name in LABEL_STATIONS
    }

    imagery = OSM(desired_tile_form="L")
    fig, ax = plt.subplots(
        1, 1, figsize=(10, 10), subplot_kw=dict(projection=imagery.crs)
    )
    ax.set_extent(MAP_BOUNDARIES)
    ax.add_image(imagery, 14, cmap="gray")
    xynps = ax.projection.transform_points(
        ccrs.Geodetic(),
        np.array([p[0] for p in nodes_info["pos"]]),
        np.array([p[1] for p in nodes_info["pos"]]),
    )
    pos = {
        k: (xynps[i, 0], xynps[i, 1]) for i, k in enumerate(nodes_info["id"])
    }

    sizes = _scale_range(nodes_info["size"], MIN_NODE_SIZE, MAX_NODE_SIZE)
    edge_alpha = _scale_range(weights, MIN_EDGE_ALPHA, MAX_EDGE_ALPHA)

    # Plots
    nx.draw_networkx_nodes(
        visualisation_graph,
        pos=pos,
        nodelist=nodes_info["id"],
        node_color=nodes_info["partition"],
        alpha=1.0,
        node_size=sizes,
        cmap="tab10_r",
        ax=ax,
    )
    nx.draw_networkx_edges(
        visualisation_graph,
        pos=pos,
        edge_color=EDGE_COLOUR,
        width=weights,
        alpha=edge_alpha,
        arrows=True,
        ax=ax,
    )
    nx.draw_networkx_labels(
        visualisation_graph,
        pos=pos,
        labels=labels,
        font_size=FONT_SIZE,
        ax=ax,
    )
    plt.show()
