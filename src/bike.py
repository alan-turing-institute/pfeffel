class Bike():
    def __init__(
        self,
        id
    ):
        self.id = id
        
    def get_story(self, dataset):
        bike_rides = dataset[dataset['bike_id']==self.id]
        return bike_rides
