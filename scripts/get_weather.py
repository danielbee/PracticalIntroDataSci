# The purpose of this script is to simply download weather data from all the stations listed in stations.txt

import requests
import os

dataPath = '../data/weather/'
with open(dataPath+'stations.txt') as f:
    stations = f.read().splitlines()

dataStationPath = dataPath+'stations/'
os.makedirs(dataStationPath, exist_ok=True)
for station in stations: 
    req = requests.get('https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/'+station+'data.txt')
    # Just write the file directly without modification.
    open(dataStationPath+station+'.txt', 'w').write(req.text)

#print(stationData)

#print(station.text)

