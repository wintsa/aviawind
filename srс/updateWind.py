import requests, os
from datetime import datetime

def downloadFile(url, file):
    r = requests.get(url, allow_redirects=True)
    open(file, 'wb').write(r.content)

def loadHpa(date, hour, hpa, type):
    filename = type + str(hpa) + ".grib2"
    downloadFile(
        "https://dd.weather.gc.ca/model_gem_global/15km/grib2/lat_lon/00/" + hour + "/CMC_glb_" + type.upper() + "GRD_ISBL_" + str(
            hpa) + "_latlon.15x.15_" + date + "00_P" + hour + ".grib2", filename)
    os.system('raster2pgsql -M -a ' + filename + ' > ' + filename + '.sql')
    os.system('sudo -u postgres psql -c "truncate ' + type + str(hpa) + '" -d avia')
    os.system('sudo -u postgres psql -f ' + filename + '.sql -d avia')
    os.system('sudo -u postgres psql -c "call recalc()" -d avia')
    os.system('rm '+filename)
    os.system('rm '+filename+'.sql')

hpas = [500, 400, 350, 300, 275, 250, 225, 200, 175, 150, 100]

now = datetime.now()
date = now.strftime("%Y%m%d")
hour = (now.hour // 3) * 3
if hour < 10:
    hour = '00' + str(hour)
else:
    hour = '0' + str(hour)

for hpa in hpas:
    loadHpa(date, hour, hpa, 'u')
    loadHpa(date, hour, hpa, 'v')
