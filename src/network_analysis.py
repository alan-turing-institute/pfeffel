from datetime import datetime

import pandas as pd
from matplotlib import pyplot as plt

from src.network import create_network_and_map

DATA_FILE = "../data/cleaned_data_20220615_1137.pickle"
# DATA_FILE = "../data/cleaned_data_20220615_1137_sample.pickle"

HARD_START_DATE = datetime(year=2010, month=1, day=1)

start_date = datetime(year=2021, month=1, day=1)
end_date = datetime(year=2022, month=1, day=1)

df = pd.read_pickle(DATA_FILE)
df = df[
    (df["start_date"] > HARD_START_DATE) & (df["end_date"] > HARD_START_DATE)
]
df_year = df[(df["start_date"] > start_date) & (df["start_date"] < end_date)]

print("Plotting mornings")
df_year_mornings = df[
    df["start_date"].dt.hour.isin([7, 8, 9, 10])
    & df["start_date"].dt.weekday.isin((0, 1, 2, 3, 4))
]
fig, ax, nodes_info = create_network_and_map(df_year_mornings)
num_communities = len(nodes_info["partition"].unique())
print(f"Number of communities: {num_communities}")
plt.title("Weekday mornings (7-10)")
plt.savefig("latest_weekday_morning_map.svg")
# plt.show()

print("Plotting afternoons")
df_year_afternoons = df[
    df["start_date"].dt.hour.isin([15, 16, 17, 18, 19])
    & df["start_date"].dt.weekday.isin((0, 1, 2, 3, 4))
]
fig, ax, nodes_info = create_network_and_map(df_year_afternoons)
num_communities = len(nodes_info["partition"].unique())
print(f"Number of communities: {num_communities}")
plt.title("Weekday afternoons (15-19)")
plt.savefig("latest_weekday_afternoon_map.svg")
# plt.show()

print("Plotting weekends")
df_year_weekends = df[df["start_date"].dt.weekday.isin((5, 6))]
fig, ax, nodes_info = create_network_and_map(
    df_year_weekends,
    allow_self_loops=True,
)
num_communities = len(nodes_info["partition"].unique())
print(f"Number of communities: {num_communities}")
plt.title("Weekends")
plt.savefig("latest_weekends_map.svg")
# plt.show()

for year in (2013, 2015, 2018, 2020):
    print(f"Plotting {year}")
    start_date = datetime(year=year, month=1, day=1)
    end_date = datetime(year=year + 1, month=1, day=1)
    df_year = df[
        (df["start_date"] > start_date) & (df["start_date"] < end_date)
    ]
    fig, ax, nodes_info = create_network_and_map(
        df_year,
        allow_self_loops=False,
        arrows=False,
    )
    num_communities = len(nodes_info["partition"].unique())
    print(f"Number of communities: {num_communities}")
    plt.title(f"Year {year}")
    plt.savefig(f"latest_{year}_map.svg")
    # plt.show()
