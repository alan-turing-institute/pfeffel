import pandas as pd

from src.network import create_network_and_map

DATA_FILE = "../data/latest_cleaned_data_samples.pickle"

df = pd.read_pickle(DATA_FILE)
create_network_and_map(df)
