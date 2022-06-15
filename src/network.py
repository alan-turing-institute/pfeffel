import json
import pickle
import re

import networkx as nx
import pandas as pd

STATION_NAMES_FILE = "../data/station_names_20220615_1137.pickle"
STATION_COORDS_FILE = "../data/stations_loc.json"


def get_station_name(id):
    with open(STATION_NAMES_FILE, "rb") as f:
        station_allnames = pickle.load(f)

    name = sorted(station_allnames[id])[0]
    name = re.split(";|,|:", name)[0]
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

    station_sizes = [i[1] for i in list(graph.out_degree(weight="trip_count"))]

    labels = [get_station_name(int(node)) for node in nodes]

    nodes_df = pd.DataFrame(
        {"id": list(nodes), "pos": pos, "size": station_sizes, "name": labels}
    )

    return nodes_df


def network_community_detection(network):
    pass


def visualise_network_map(network, node_pos, node_label):
    # partition = community_louvain.best_partition(G)
    pass


def main():

    data = pd.read_pickle("../test/data/sample.pickle")
    graph = create_network_from_data(data, 0.001)

    nodes_info = get_node_info(graph)

    print(nodes_info)


if __name__ == "__main__":
    main()
