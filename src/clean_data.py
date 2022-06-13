import datetime
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

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


def clean_datetime_column(df, colname, roundto="S"):
    """Parse df[colname] from strings to datetime objects, and round the times
    to the nearest hour. Also chop off from df any rows with times before
    2010-07-30 or after 2020-01-01, since these are nonsense. df is partially
    modified in place, but the return value should still be used.
    """
    # A bit of a hacky way to use the first entry to figure out which date
    # format this file uses. Not super robust, but works for our purposes.
    if len(df[colname].iloc[0]) > 16:
        format = "%d/%m/%Y %H:%M:%S"
    else:
        format = "%d/%m/%Y %H:%M"
    df[colname] = pd.to_datetime(df[colname], format=format)
    df[colname] = df[colname].dt.round(roundto)
    early_cutoff = datetime.datetime(2010, 7, 30)  # When the program started.
    late_cutoff = datetime.datetime.now()
    df = df[(late_cutoff > df[colname]) & (df[colname] >= early_cutoff)]
    return df


def castable_to_int(obj):
    """Return True if obj is castable to int, False otherwise."""
    try:
        int(obj)
        return True
    except ValueError:
        return False


def cast_to_int(df, colname):
    """Cast df[colname] to dtype int. All rows that are not castable to int are
    dropped. df is partially modified in place, but the return value should be
    used.
    """
    try:
        df = df.astype({colname: np.int_}, copy=False)
    except ValueError:
        castable_rows = df[colname].apply(castable_to_int)
        df = df[castable_rows]
        df = df.astype({colname: np.int_}, copy=False)
    return df


def load_clean_data(bikefolder="./bikes", num_files=None):
    """Load the cleaned bike usage data from disk, return a pd.DataFrame.

    Args:
      bikefolder: Path to where the data is kept. Default: "./bikes?
      N_files: Number of data files to load. Default: all
            (which probably won't fit in
      memory!)
    """
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

    # Each CSV file will list events in some time window. We process them
    # one-by-one, collect all the DataFrames for individual time windows to
    # `pieces`, and concatenate them at the end.

    pieces = []
    # Columns of the CSV files that we need.
    cols = [
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
    # At least one CSV file gives us trouble because it doesn't list station
    # IDs, only station names. We'll collect the paths to those CSV files to
    # `problem_paths` and deal with them at the end.
    problem_paths = []
    for path in datapaths:
        print("Processing {}".format(path))
        try:
            df = pd.read_csv(path, usecols=cols, encoding="ISO-8859-2")
        except ValueError:
            # Some files have missing or abnormaly named columns. We'll deal
            # with them later.
            problem_paths.append(path)
            continue
        # Cast the columns to the right types. This is easier ones NAs have
        # been dropped.
        df = cast_to_int(df, "EndStation Id")
        df = cast_to_int(df, "StartStation Id")
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
    # ID columns.  They do have the station names though, so we'll use those
    # to, with the above dictionary to get the IDs.
    # print("Doing the problem cases ({} of them).".format(len(problem_paths)))
    safe_cols = [
        "Duration",
        "Bike Id",
        "End Date",
        "EndStation Name",
        "Start Date",
        "StartStation Name",
    ]
    for path in problem_paths:
        print(path)
        df = pd.read_csv(path, usecols=safe_cols, encoding="ISO-8859-2")
        # Add a column of station IDs, based on names.
        df["EndStation Id"] = df["EndStation Name"].apply(get_station_id)
        df["StartStation Id"] = df["StartStation Name"].apply(get_station_id)
        # Turn the date columns from strings into datetime objects rounded to
        # the hour.
        clean_datetime_column(df, "End Date")
        clean_datetime_column(df, "Start Date")
        pieces.append(df)

    df = pd.concat(pieces)
    df = df.rename(columns=COLUMN_RENAMES)
    df = df.sort_values("rental_id")
    df = df.set_index("rental_id")
    return df


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
        station["commonName"]: {"lat": station["lat"], "lon": station["lon"]}
        for station in stations
    }
    with open("../test/data/stations_loc.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)
