import pandas as pd 
import bike 

df = pd.read_csv('../test/data/9. Journey Data Extract 19Aug-20 Aug12.csv',sep=',')

bike = bike.Bike(id=8710)
bike_story = bike.get_story(df)

print (bike_story.head())
