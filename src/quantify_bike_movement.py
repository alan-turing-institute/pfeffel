import h3


def get_chain_total_ditance(df):
    return df["distance"].sum()


def get_chain_distance_vs_length(df, option="total"):
    distance = []
    chain_size = []
    for name, group in df.groupby("chain_id"):
        chain_size.append(group.shape[0])
        if option == "total":
            distance.append(get_chain_total_ditance(group))
        elif option == "start_end_distance":
            distance.append(get_chain_total_ditance(group))
        else:
            print("Only total or start_end_distance are avalaible")

    return {"distance": distance, "chain_size": chain_size}


def get_number_of_areas_on_chain(df):
    pass


def get_probability_of_leaving_area(df):
    pass


def get_distance_start_end_chain(df):
    if df.shape[0] == 1:
        return 0
    else:
        df.sort_values(by="start_date", ascending=True)
        start_loc = (
            df.iloc[0]["start_station_lat"],
            df.iloc[0]["start_station_lon"],
        )
        end_loc = (
            df.iloc[-1]["end_station_lat"],
            df.iloc[0]["end_station_lon"],
        )
        distance = h3.point_dist(start_loc, end_loc, unit="m")

        return distance
