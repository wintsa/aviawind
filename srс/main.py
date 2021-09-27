import json
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt

def getAircrafts():
    aircrafts = pd.read_csv(r'../data/aircraftDatabase-2021-09.csv')[['manufacturericao', 'icao24', 'typecode']]
    value_list = ['BOEING', 'AIRBUS', 'RAYTHEON', 'EMBRAER', 'LEARJET']
    boolean_series = aircrafts.manufacturericao.isin(value_list)
    aircrafts = aircrafts[boolean_series][['icao24', 'typecode']]
    return aircrafts


# print(aircrafts)

def getAircraftSpeed(aircrafts):
    aircraftModelSpeeds = pd.read_csv(r'../data/speed.csv')  # [['model', 'speed']]
    aircraftSpeeds = pd.merge(aircrafts, aircraftModelSpeeds, on="typecode")
    speedDict = dict()
    for a in aircraftSpeeds.to_dict('records'):
        speedDict[a['icao24']] = a['speed']
    return speedDict


# [['model', 'icao24']]
# print(v)
# https://opendata.dwd.de/weather/nwp/icon/grib/00/u/
# https://d-nb.info/1081305452/34
# https://opensky-network.org/apidoc/rest.html
# print(df)

def loadStates():
    #    data = urllib.request.urlopen("https://opensky-network.org/api/states/all").read()
    #    with open('temp.json', 'wb') as file:
    #        file.write(data)
    with open('temp.json', 'rb') as fin:
        data = fin.read()
    output = json.loads(data)
    states = output["states"]
    return states


def getTable(states, speedDict):
    cnt = 0
    cntGood = 0
    listVel = []
    for state in states:
        icao = state[0]
        x = state[5]
        y = state[6]
        z = state[13]
        velocity = state[9]
        deg = state[10]
        speed = speedDict.get(icao)
        cnt = cnt + 1
        if x is None or y is None or z is None or velocity is None or deg is None or speed is None or z < 8000:
            continue
        cntGood = cntGood + 1
#        if cntGood < 100:
        windVelocity = velocity * 3.6 - speed
        listVel.append(windVelocity)
#            print(icao, x, y, z, deg, round(windVelocity, 2))
    windVelData = pd.DataFrame(listVel)
    return windVelData
#    print(temp2)
    #print(cntGood, cnt)


aircrafts = getAircrafts()
speedDict = getAircraftSpeed(aircrafts)
states = loadStates()

windVelData = getTable(states, speedDict)
'''
cnt = len(states)
cntgood = 0
cntInAircrafts = 0

t = aircrafts['icao24'].to_dict().values()

num = 100
for a in states:
    icao = a[0]
    good = False
    if icao in t:
        cntInAircrafts += 1
        good = True
    if icao in speedDict:
        cntgood += 1
    else:
        if num > 0 and good:
            print(a)
            num = num - 1
print(cntInAircrafts, cntgood, cnt)
'''
