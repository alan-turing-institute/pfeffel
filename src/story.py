import pandas as pd 
import bike, clean_data

data = clean_data.load_clean_data('../test/data')

bike = bike.Bike(id=8710)
bike_story = bike.get_story(data)
bike_usage = bike.get_usage(bike_story)

print (bike_usage)
