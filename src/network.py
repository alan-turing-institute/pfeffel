import json
import pickle
import re

import community
import networkx as nx
import pandas as pd

STATION_NAMES_FILE = "../data/station_names_20220615_1137.pickle"
STATION_COORDS_FILE = "../data/stations_loc.json"


def get_station_name(id):
    with open(STATION_NAMES_FILE, "rb") as f:
        station_allnames = pickle.load(f)

    name = sorted(station_allnames[id])[0]
    name = re.split(";|,|:", name)[0].strip()
    return name


def create_network_from_data(df, TRIP_COUNT_THRESHOLD):
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
        trip_counts["trip_count"] >= TRIP_COUNT_THRESHOLD * total_num_trips
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
