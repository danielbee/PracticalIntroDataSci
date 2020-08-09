# The data

Monthly data are available for a selection of long-running historic stations. The series typically range from 50 to more than 100 years in length.

Our historic station data consists of:

1. Mean daily maximum temperature (tmax)
1. Mean daily minimum temperature (tmin)
1. Days of air frost (af)
1. Total rainfall (rain)
1. Total sunshine duration (sun)
The monthly mean temperature is calculated from the average of the mean daily maximum and mean daily minimum temperature i.e. (tmax+tmin)/2.

Missing data (more than two days missing in a month) have been indicated by "---". Estimated data (where available) have been indicated by "*" after the value.

Sunshine data using a Kipp and Zonen sensor have been indicated by a "#" after the value. All other sunshine data have been recorded using a Campbell-Stokes recorder.

Station data files are updated on a rolling monthly basis, around 10 days after the end of the month. Data are indicated as provisional until the full network quality control has been carried out. After this, data are final.

No allowances have been made for small site changes and developments in instrumentation. Data and statistics for other stations, and associated charges, can be obtained by contacting our Customer Centre.


# Links

Retrevied from https://www.metoffice.gov.uk/research/climate/maps-and-data/historic-station-data

## Station specific data downloads
https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/nairndata.txt

https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/<station_name>data.txt

Station names are given at stations.txt

### Stations.txt content
* aberporth
* armagh
* ballypatrick
* bradford
* braemar
* camborne
* cambridge
* cardiff
* chivenor
* cwmystwyth
* dunstaffnage
* durham
* eastbourne
* eskdalemuir
* heathrow
* hurn
* lerwick
* leuchars
* lowestoft
* manston
* nairn
* newtonrigg
* oxford
* paisley
* ringway
* rossonwye
* shawbury
* sheffield
* southampton
* stornoway
* suttonbonington
* tiree
* valley
* waddington
* whitby
* wickairport
* yeovilton

# Usage

This repo has a script to collect all data, then maybe concat just the data tables, but with new columns.
1. station
1. lat_f
1. long_f
1. lat_s
1. long_s
1. amsl
Where :
* Lat and Long are the latitude and longitude 
    * lat_f is in a float in degrees (57.593,-3.821) . 
    * lat_s is a string like 291200E
* asml is height above sea level in meters. 

Note, these new columns may be important as, for a given station, the location may change and therefore introduce a skew. 
* I'd image that height above sea level may affect weather conditions significantly, so simply relying on station name is not wise. 


Then another script, which does the analysis (notebook) will construct a MultiIndex DataFrame. 
multi index is this hiearchy
* station, yyyy, mm 

