import pandas as pd


def loadData():
    df = pd.read_csv(r'../data/aircraftDatabase-2021-09.csv')
    value_list = ['BOEING', 'AIRBUS', 'RAYTHEON', 'EMBRAER', 'LEARJET']
    boolean_series = df.manufacturericao.isin(value_list)
    df = df[boolean_series]
    return df

def printManufacturerStat(df):
    v = df[['manufacturericao', 'icao24']] \
        .groupby('manufacturericao') \
        .count() \
        .sort_values("icao24", ascending=False)
    v = v.loc[v["icao24"] > 100]
    print(len(v))
    print(v.head(20))

def printListModels(df):
    v = df[['manufacturericao','typecode', 'icao24']] \
        .groupby(['manufacturericao','typecode']) \
        .count() \
        .sort_values("icao24", ascending=False)
    print(len(v))
    # print(v.head(20))
    for a in v.index.sort_values():
        print(a[0], a[1], sep=',', end=',800\n')


df = loadData()
print(df)
printListModels(df)


