import json
import urllib.request
import pandas as pd

df = pd.read_csv (r'../data/aircraftDatabase-2021-09.csv')
cnt = len(df)
print(df.groupby('model').count().sort_values("icao24", False))
#https://opendata.dwd.de/weather/nwp/icon/grib/00/u/
#https://d-nb.info/1081305452/34
#https://opensky-network.org/apidoc/rest.html
#print(df)

#data = urllib.request.urlopen("https://opensky-network.org/api/states/all").read()
#output = json.loads(data)
#states = output["states"]

#cnt = len(states)
print(cnt)
