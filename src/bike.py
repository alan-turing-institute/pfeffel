class Bike:
    def __init__(self, id):
        self.id = id

    def get_story(self, dataset):
        bike_rides = dataset[dataset["bike_id"] == self.id]
        bike_rides["usage"] = bike_rides.apply(
            lambda row: row["end_date"] - row["start_date"], axis=1
        )
        return bike_rides

    def get_usage(self, bike_rides):
        usage = bike_rides["usage"].sum()
        return usage
