import requests as requests

class Trip:

    def __init__(self, data, trip_id, station_data):
        df = data[data.index == trip_id]

        self.init_station = {'name': df.start_station_name.values[0], 'id': df.start_station_id.values[0],
                             'latitude': station_data[df.start_station_name.values[0]]['lat'],
                             'longitude':station_data[df.start_station_name.values[0]]['lon']}
        self.end_station = {'name': df.end_station_name.values[0], 'id': df.end_station_id.values[0],
                            'latitude': station_data[df.end_station_name.values[0]]['lat'],
                            'longitude': station_data[df.end_station_name.values[0]]['lon']}
        self.bike = df.bike_id.values[0]
        self.duration = df.duration.values[0]
        self.date = {'start': df.start_date.values[0], 'end': df.end_date.values[0]}




    # def get_route(self):
    #     registeredapikey = 'f339aa90aba2b309'
    #     trip = 'https: //www.cyclestreets.net/api/journey.json?key='+registeredapikey+'&reporterrors=1&itinerarypoints =0.11795,52.20530'
    #     response = requests.get(name)
    #
    #     name = 'https://www.cyclestreets.net/api/journey.json?key=f339aa90aba2b309&reporterrors=1&start='+self.init_station['name']+'&end='+self.end_station['name']+'&plan=quietest'
    #     #print (response)
    #



