import datetime
from operator import itemgetter
import json
import urllib.request
import pandas as pd
from math import sqrt
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def getAircrafts():
    """
    aircrafts = pd.read_csv(r'../data/aircraftDatabase-2021-09.csv')[['manufacturericao', 'icao24', 'typecode']]
    value_list = ['BOEING', 'AIRBUS', 'RAYTHEON', 'EMBRAER', 'LEARJET']
    boolean_series = aircrafts.manufacturericao.isin(value_list)
    aircrafts = aircrafts[boolean_series][['icao24', 'typecode']]
    aircrafts.to_csv(r'../data/aircrafts.csv', index=False)
    """
    aircrafts = pd.read_csv(r'../data/aircrafts.csv')
    return aircrafts


# print(aircrafts)

def getAircraftSpeed(aircrafts):
    aircraftModelSpeeds = pd.read_csv(r'../data/speed.csv')  # [['model', 'speed']]
    aircraftSpeeds = pd.merge(aircrafts, aircraftModelSpeeds, on="typecode")
    speedDict = dict()
    for a in aircraftSpeeds.to_dict('records'):
        speedDict[a['icao24']] = a['speed']
    return speedDict


# levels = pd.read_csv(r'../data/levels.csv')
levels = {500: 5570,
          400: 7180,
          350: 8110,
          300: 9160,
          275: 9740,
          250: 10360,
          225: 11030,
          200: 11770,
          175: 12590,
          150: 13500,
          100: 15790}


def getLevel(z):
    plev = 0
    phpa = 1000
    for hpa, lev in levels.items():
        if lev > z:
            return hpa, phpa, float(z - plev) / (lev - plev)
        phpa = hpa
        plev = lev
    return 350, 300, 1


# [['model', 'icao24']]
# print(v)
# https://opendata.dwd.de/weather/nwp/icon/grib/00/u/
# https://d-nb.info/1081305452/34
# https://opensky-network.org/apidoc/rest.html
# print(df)

def loadStates():
    # data = urllib.request.urlopen("https://opensky-network.org/api/states/all").read()
    # with open('temp.json', 'wb') as file:
    #        file.write(data)
    with open('temp.json', 'rb') as fin:
        data = fin.read()
    output = json.loads(data)
    states = output["states"]
    return states


def getVelocityFromDB(conn, x, y, z):
    point = f"ST_MakePoint({x}, {y})"
    l1, l2, d = getLevel(z)
    #    print(z, l1, levels[l1], l2, levels[l2], d)
    result_set = conn.execute(
        f"""with d as (
select ua.rid as ua, ub.rid as ub, va.rid as va, vb.rid as vb
from u300 ua join u350 ub using (minx, miny, maxx, maxy)
join v300 va using (minx, miny, maxx, maxy)
join v350 vb using (minx, miny, maxx, maxy)
where {x}>=minx and {x}<=maxx and {y}>=miny and {y}<=maxy
)
select ST_Value(ua.rast, {point}),
ST_Value(va.rast, {point}),
ST_Value(ub.rast, {point}),
ST_Value(vb.rast, {point})
from d
join u300 ua on ua.rid=ua
join v300 va on va.rid=va
join u350 ub on ub.rid=ub
join v350 vb on vb.rid=vb""")
    for r in result_set:
        return sqrt(r[0] * r[0] + r[1] * r[1]) * d + sqrt(r[0] * r[0] + r[1] * r[1]) * (1 - d)


def saveVelocity(conn, t, x, y, z, velocity, speed, prognosisVelocit):
    pass


'''    conn.execute(
        f"""insert into planes (t, z, planeVelocity, observedVelocity, windVelocity, v, geom) values
        ('{t}'::timestamp, {z}, {speed}, {velocity}, {prognosisVelocit}, {velocity - speed - prognosisVelocit}, ST_MakePoint({x},{y}))""")
'''


def saveInfo(conn, info):
    s = "insert into planes (t, z, planeVelocity, observedVelocity, windVelocity, v, geom) values "
    first = True
    for state in info:
        if first:
            first = False
        else:
            s += ",\n"
        s += "('" + str(state[0]) + "'::timestamp, " + str(state[3]) + ", " + str(state[5]) + ", " + str(
            state[4]) + ", " + str(state[6]) + ", " + str(state[4] - state[5] - state[6]) + ", ST_MakePoint(" + str(
            state[1]) + "," + str(state[2]) + "))"
    conn.execute(s)


def getTable(states, speedDict, t):
    cnt = 0
    requestCount = 0
    cntGood = 0
    listVel = []
    db = create_engine("postgresql://avia:q@localhost:5437/avia")
    info = []
    with db.connect() as conn:
        for state in states:
            icao = state[0]
            x = state[5]
            y = state[6]
            z = state[13]
            velocity = state[9]  # m/s
            deg = state[10]
            speed = speedDict.get(icao)
            cnt = cnt + 1
            if x is None or y is None or z is None or velocity is None or deg is None or speed is None or z < 8000:
                continue
            speed = speed / 3.6  # m/s
            cntGood = cntGood + 1
            #        if cntGood < 100:
            windVelocity = velocity - speed  # m/s
            prognosisVelocity = getVelocityFromDB(conn, x, y, z)
            if prognosisVelocity is not None:
                errorWindVelocity = windVelocity - prognosisVelocity
                listVel.append(errorWindVelocity)
                info.append([t, x, y, z, velocity, speed, prognosisVelocity]);
            #                saveVelocity(conn, t, x, y, z, velocity, speed, prognosisVelocity)
            requestCount += 1
            if requestCount % 100 == 0:
                print(requestCount)
        #            print(icao, x, y, z, deg, round(windVelocity, 2))
        saveInfo(conn, info)


#    windVelData = pd.DataFrame(listVel)
#    return windVelData


#    print(temp2)
# print(cntGood, cnt)

t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

aircrafts = getAircrafts()
speedDict = getAircraftSpeed(aircrafts)
states = loadStates()

states = filter(lambda state: state[13], states)
states = sorted(states, key=itemgetter(13))

windVelData = getTable(states, speedDict, t)
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

# dd.weather.gc.ca/model_gem_global/15km/grib2/lat_lon/
# 00/$shift$/CMC_glb_DEPR_ISBL_$level$_latlon.15x.15_$date$00_P$shift$.grib2
