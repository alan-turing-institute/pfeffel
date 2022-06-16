import cartopy.crs as ccrs
import networkx as nx
import numpy as np
import pandas as pd
from cartopy.io.img_tiles import OSM
from matplotlib import pyplot as plt

from src.network import (
    create_network_from_data,
    get_node_info,
    network_community_detection,
)

DATA_FILE = "../data/latest_cleaned_data_samples.pickle"
TRIP_COUNT_THRESHOLD = 2e-5
NUM_LABELS = 16
FONT_SIZE = 10
EDGE_WIDTH_FACTOR = 1e-2
MAX_NODE_SIZE = 150.0
MIN_NODE_SIZE = 0.1
MIN_EDGE_ALPHA = 0.1
MAX_EDGE_ALPHA = 0.9
EDGE_COLOUR = "#222222"


def scale_range(values, min_scaled, max_scaled):
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


df = pd.read_pickle(DATA_FILE)
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
    for id, name in zip(
        nodes_info["id"][:NUM_LABELS], nodes_info["name"][:NUM_LABELS]
    )
}

imagery = OSM()
fig, ax = plt.subplots(
    1, 1, figsize=(10, 10), subplot_kw=dict(projection=imagery.crs)
)
ax.set_extent((-0.24, 0.02, 51.45, 51.56))
ax.add_image(imagery, 14)
xynps = ax.projection.transform_points(
    ccrs.Geodetic(),
    np.array([p[0] for p in nodes_info["pos"]]),
    np.array([p[1] for p in nodes_info["pos"]]),
)
pos = {k: (xynps[i, 0], xynps[i, 1]) for i, k in enumerate(nodes_info["id"])}

sizes = scale_range(nodes_info["size"], MIN_NODE_SIZE, MAX_NODE_SIZE)
edge_alpha = scale_range(weights, MIN_EDGE_ALPHA, MAX_EDGE_ALPHA)

# Plots
nx.draw_networkx_nodes(
    visualisation_graph,
    pos=pos,
    nodelist=nodes_info["id"],
    node_color=nodes_info["partition"],
    alpha=1.0,
    node_size=sizes,
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
