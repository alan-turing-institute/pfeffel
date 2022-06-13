import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

# Columns of the CSV files that we need, and some data relate to them.
COLUMNS = [
    "Rental Id",
    "Duration",
    "Bike Id",
    "End Date",
    "EndStation Id",
    "EndStation Name",
    "Start Date",
    "StartStation Id",
    "StartStation Name",
]
COLUMNS_ALTERNATIVE_NAMES = {
    "Duration": ("Duration_Seconds",),
    "EndStation Id": ("End Station Id",),
    "EndStation Name": ("End Station Name",),
    "StartStation Id": ("Start Station Id",),
    "StartStation Name": ("Start Station Id",),
}
COLUMN_RENAMES = {
    "Rental Id": "rental_id",
    "Duration": "duration",
    "Bike Id": "bike_id",
    "End Date": "end_date",
    "EndStation Id": "end_station_id",
    "EndStation Name": "end_station_name",
    "Start Date": "start_date",
    "StartStation Id": "start_station_id",
    "StartStation Name": "start_station_name",
}
COLUMN_DTYPES = {
    "Rental Id": np.float_,
    "Duration": np.float_,
    "Bike Id": np.float_,
    "End Date": str,
    "EndStation Id": np.float_,
    "EndStation Name": str,
    "Start Date": str,
    "StartStation Id": np.float_,
    "StartStation Name": str,
}


def add_station_names(station_names, df, namecolumn, idcolumn):
    """Given a DataFrame df that has df[namecolumn] listing names of stations
    and df[idcolumn] listing station ID numbers, add to the dictionary
    station_names all the names that each ID is attached to.
    """
    namemaps = (
        df[[idcolumn, namecolumn]]
        .groupby(idcolumn)
        .aggregate(lambda x: x.unique())
    )
    for number, names in namemaps.iterrows():
        current_names = station_names.get(number, set())
        # The following two lines are a stupid dance around the annoying fact
        # that pd.unique sometimes returns a single value, sometimes a numpy
        # array of values, but since the single value is a string, it too is an
        # iterable.
        vals = names[0]
        new_names = set([vals]) if type(vals) == str else set(vals)
        current_names.update(new_names)
        station_names[number] = current_names


def clean_datetime_column(df, colname, roundto="min"):
    """Parse df[colname] from strings to datetime objects, and round the times
    to the nearest minute. df is partially modified in place, but the return
    value should still be used.
    """
    # A bit of a hacky way to use the first entry to figure out which date
    # format this file uses. Not super robust, but works for our purposes.
    if len(df[colname].iloc[0]) > 16:
        format = "%d/%m/%Y %H:%M:%S"
    else:
        format = "%d/%m/%Y %H:%M"
    df[colname] = pd.to_datetime(df[colname], format=format)
    df[colname] = df[colname].dt.round(roundto)
    return df


def load_clean_data(bikefolder="./bikes", num_files=None, datapaths=None):
    """Load the cleaned bike usage data from disk.

    Return a pd.DataFrame and a dictionary mapping station IDs to all names
    they are known by.

    Args:
      bikefolder: Path to where the data is kept. Default: "./bikes?
      num_files: Number of data files to load. Default: all (which probably
      won't fit in memory!)
      datapaths: A list of filenames to load. Default: all. Overrides the other
      arguments if set.
    """
    if datapaths is None:
        # Collect the paths to all the CSV files.
        datafiles = sorted(os.listdir(bikefolder))
        if num_files is not None:
            datafiles = datafiles[:num_files]
        folderpath = Path(bikefolder)
        datapaths = [folderpath / Path(file) for file in datafiles]
        datapaths = [p for p in datapaths if p.suffix == ".csv"]

    # Initialize a dictionary that will have as keys station ID numbers, and as
    # values sets that include all the names this station has had in the files.
    station_allnames = {}

    # Each CSV file will list trips in some time window. We process them
    # one-by-one, collect all the DataFrames for individual time windows to
    # `pieces`, and concatenate them at the end.
    pieces = []
    # At least one CSV file gives us trouble because it doesn't list station
    # IDs, only station names. We'll collect the paths to those CSV files to
    # `problem_paths` and deal with them at the end.
    problem_paths = []
    for path in datapaths:
        print("Processing {}".format(path))
        try:
            df = pd.read_csv(
                path,
                usecols=COLUMNS,
                encoding="ISO-8859-2",
                dtype=COLUMN_DTYPES,
            )
        except ValueError:
            # Some files have missing or abnormaly named columns. We'll deal
            # with them later.
            problem_paths.append(path)
            continue
        # Drop all rows where all values are missing. There literally are lines
        # in the CSV files that specify such empty rows.
        df = df[~df.isna().all(axis=1)]
        df["filename"] = path
        # Turn the date columns from strings into datetime objects rounded to
        # the hour.
        df = clean_datetime_column(df, "End Date")
        df = clean_datetime_column(df, "Start Date")
        pieces.append(df)

        # Add station names appearing in this file to our collection of names.
        add_station_names(
            station_allnames, df, "EndStation Name", "EndStation Id"
        )
        add_station_names(
            station_allnames, df, "StartStation Name", "StartStation Id"
        )

    # Now that we've collected all the different names that the same station
    # goes by, we'll pick one of them to be the name we'll use. We do this by
    # just picking the one that is alphabetically first. We'll also make a
    # dictionary that goes the other way around, for each name it gives the
    # corresponding station ID.
    station_ids = {}
    station_names = {}
    for k, v in station_allnames.items():
        v = sorted(v)
        station_names[k] = v[0]
        for name in v:
            station_ids[name] = k

    def get_station_id(name):
        try:
            return station_ids[name]
        except KeyError:
            return np.nan

    # Let's deal with the problem cases. They are ones that are missing station
    # ID columns. They do have the station names though, so we'll use those,
    # with the above dictionary, to get the IDs.
    print("Doing the problem cases ({} of them).".format(len(problem_paths)))
    for path in problem_paths:
        print(path)
        df = pd.read_csv(
            path,
            encoding="ISO-8859-2",
        )
        # Drop all rows where all values are missing. There literally are lines
        # in the CSV files that specify such empty rows.
        df = df[~df.isna().all(axis=1)]
        df["filename"] = path
        # If one of the expected columns is missing, look for alternative names
        # for it.
        for column_name in COLUMNS:
            if (
                column_name not in df.columns
                and column_name in COLUMNS_ALTERNATIVE_NAMES
            ):
                for alternative_name in COLUMNS_ALTERNATIVE_NAMES[column_name]:
                    if alternative_name in df.columns:
                        df[column_name] = df[alternative_name]
        # Remove all the columns that we didn't expect.
        for column_name in df.columns:
            if column_name not in COLUMNS:
                df = df.drop(columns=column_name)
        # Add a column of station IDs, based on names.
        if "EndStation Id" not in df.columns:
            df["EndStation Id"] = df["EndStation Name"].apply(get_station_id)
        if "StartStation Id" not in df.columns:
            df["StartStation Id"] = df["StartStation Name"].apply(
                get_station_id
            )
        # Turn the date columns from strings into datetime objects rounded to
        # the hour.
        df = clean_datetime_column(df, "End Date")
        df = clean_datetime_column(df, "Start Date")
        pieces.append(df)

    df = pd.concat(pieces)

    # If station ID isn't there, but name is, fill the ID using the name.
    filter = ~df["StartStation Name"].isna() & df["StartStation Id"].isna()
    df.loc[filter, "StartStation Id"] = df.loc[
        filter, "StartStation Name"
    ].apply(get_station_id)
    filter = ~df["EndStation Name"].isna() & df["EndStation Id"].isna()
    df.loc[filter, "EndStation Id"] = df.loc[filter, "EndStation Name"].apply(
        get_station_id
    )

    df = df.rename(columns=COLUMN_RENAMES)
    df = df.convert_dtypes()  # Convert floats to ints, with NaN -> NA
    # We don't consider dates when dropping duplicates, because they may be
    # rounded in different ways in different files.
    df = df.drop_duplicates(
        subset=[
            "rental_id",
            "bike_id",
            "end_station_id",
            "start_station_id",
        ]
    )
    df = df.sort_values("rental_id")
    df = df.set_index("rental_id")
    return df, station_allnames


def clean_station_json(filepath):
    """
    Given an input json files with station information
    (downloaded from here:
    https://api.tfl.gov.uk/swagger/ui/index.html?url=/swagger/docs/v1#!/BikePoint/BikePoint_GetAll) # noqa: E501
    Produce a simple json with {station_name:{"lat":lat,"lon":lon}}
    Args:
        filepath (str): path to the json file
    """
    with open(filepath) as f:
        stations = json.load(f)
    dataset = {
        station["id"].split("_")[1]: {
            "lat": station["lat"],
            "lon": station["lon"],
        }
        for station in stations
    }
    with open("../test/data/stations_loc.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)
