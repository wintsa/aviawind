import json
import urllib.request
import pandas as pd


aircrafts = pd.read_csv (r'../data/aircraftDatabase-2021-09.csv')[['manufacturericao', 'icao24', 'model']]
value_list = ['BOEING', 'AIRBUS', 'RAYTHEON', 'EMBRAER', 'LEARJET']
boolean_series = aircrafts.manufacturericao.isin(value_list)
aircrafts = aircrafts[boolean_series][['icao24', 'model']]
#print(aircrafts)

aircraftModelSpeeds = pd.read_csv (r'../data/speed.csv')# [['model', 'speed']]
#print(aircraftModelSpeeds)

aircraftSpeeds = pd.merge(aircrafts, aircraftModelSpeeds, on="model")
r = dict()
for a in aircraftSpeeds.to_dict('records'):
    r[a['icao24']] = a['speed']
#print(aircraftSpeeds)
'''
df = pd.read_csv (r'../data/aircraftDatabase-2021-09.csv')
value_list = ['BOEING', 'AIRBUS', 'RAYTHEON', 'EMBRAER', 'LEARJET']
boolean_series = df.manufacturericao.isin(value_list)
df = df[boolean_series]

v = df[['manufacturericao', 'icao24']]\
    .groupby('manufacturericao')\
    .count()\
    .sort_values("icao24", ascending=False)
#print(v)
v = v.loc[v["icao24"]>100]
print(len(v))
print(v.head(20))
1/0


print(df)
cnt = len(df)
v = df[['model', 'icao24']]\
    .groupby('model')\
    .count()\
    .sort_values("icao24", ascending=False)

v = v.loc[v["icao24"]>100]

print(len(v))

#print(v.head(20))

print(v.index.sort_values())
'''
#[['model', 'icao24']]
#print(v)
#https://opendata.dwd.de/weather/nwp/icon/grib/00/u/
#https://d-nb.info/1081305452/34
#https://opensky-network.org/apidoc/rest.html
#print(df)

data = urllib.request.urlopen("https://opensky-network.org/api/states/all").read()
output = json.loads(data)
states = output["states"]

cnt = len(states)
cntgood = 0
for a in states:
    icao = a[0]
    if icao in r:
        cntgood += 1
print(cntgood, cnt)
