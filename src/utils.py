import seaborn as sns


def get_colours(steps):
    colours = sns.color_palette("mako").as_hex()
    rev_colours = sns.color_palette("mako").as_hex()
    rev_colours.reverse()
    colours = rev_colours + colours
    while len(colours) < steps:
        colours += colours
    return colours


def traj_to_timestamped_geojson(trajectory):
    features = []
    df = trajectory.df.copy()
    df["previous_geometry"] = df["geometry"].shift()
    df["time"] = df.index
    df["previous_time"] = df["time"].shift()
    for _, row in df.iloc[1:].iterrows():
        coordinates = [
            [
                row["previous_geometry"].xy[0][0],
                row["previous_geometry"].xy[1][0],
            ],
            [row["geometry"].xy[0][0], row["geometry"].xy[1][0]],
        ]
        times = [row["previous_time"].isoformat(), row["time"].isoformat()]
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates,
                },
                "properties": {
                    "times": times,
                    "style": {
                        "color": row["colour"],
                        "weight": 5,
                    },
                },
            }
        )
    return features
