from unittest import TestCase

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.quantify_bike_movement import get_chain_distance_vs_length


class TestQuantification(TestCase):
    def setUp(self):
        self.data = pd.read_pickle("data/sample.pickle")

    def test_get_chain_distance_vs_length(self):

        total_distance_vs_length = get_chain_distance_vs_length(
            self.data, "total"
        )

        distance_vs_length = get_chain_distance_vs_length(
            self.data, "start_end_distance"
        )

        sns.scatterplot(
            y=total_distance_vs_length["distance"],
            x=total_distance_vs_length["chain_size"],
        )
        sns.scatterplot(
            y=distance_vs_length["distance"],
            x=distance_vs_length["chain_size"],
        )

        plt.show()
