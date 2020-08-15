# The purpose of this script is to collect all the station data into a single data structure. 
# This will require regular expressions to find things like station changes. 

#the hope is that we can simply export this single data structure to a single file is whatever format we want. 

# Need to figure out how to deal with 'null' values. 
import re

import pandas as pd

def main(): 

    dataPath = '../data/weather/'
    dataStationPath = dataPath+'stations/'
    with open(dataPath+'stations.txt') as f:
        stations = f.read().splitlines()
    bigFrame = []
    stationDataRaw = {}
    for station in stations: 
        print(station)
        stationDataRaw[station]= open(dataStationPath+station+'.txt').read().splitlines()
        extras = getDataExtras(stationDataRaw[station])
        stationFrame = getDataFrame(stationDataRaw[station])
        # add a column for the station
        stationFrame['station'] = station
        # Make station column the most signifiant index in the multiIndex
        stationFrame.set_index(['station', stationFrame.index],inplace=True)
        # Append to list of dataframes
        bigFrame.append(stationFrame)
    # Combine all the dataframes
    stationsData = pd.concat(bigFrame)
    print(stationsData.reset_index().dtypes)
    # Print out in desired formats
    stationsData.to_excel(dataPath+'stationData.xlsx')
    stationsData.to_csv(dataPath+'stationData.csv')

# bit of an assumption
tableStart = re.compile('\s{3}yyyy')
reWord = re.compile('\w+')
reNum = re.compile('[0-9.]+')
def getDataFrame(raw):
    for ln,line in enumerate(raw):
        if re.search(tableStart,line):
            tableStartLine = ln
            # stop going through lines
            break

    table = raw[tableStartLine:]
    # remove empty string lines
    table = list(filter(None, table))
    headers= table[0].split()
    #print(headers)
    prevEnd = 0
    units = {}
    headerCols = [re.search(header,table[0]) for header in headers]
    for colI,col in enumerate(headerCols):
        units[headers[colI]] = reWord.findall(table[1],prevEnd,col.end())
        prevEnd = col.end()
    records = []
    for row in table[2:]:
        
        prevEnd = 0
        record = {}
        for colI,col in enumerate(headerCols):
            res= reNum.findall(row,prevEnd,col.end())
            
            record[headers[colI]] = res[0] if res else None
            prevEnd = col.end()
        records.append(record)
    
    df = pd.DataFrame.from_dict(records)
    df.set_index(['yyyy', 'mm'],inplace=True)
    #print(df)
    return df

import re
def getDataExtras(raw):
    topRaw = '\n'.join(raw[0:20])

    gridRef = re.findall('\d+E \d+N',topRaw)
    asml=[]
    latlon=[]
    for line in raw[0:20]:
        if re.search(gridRef[0],line):
            print(line)
           
            asml.append(re.search('(\d+)\s*m\w*\samsl',line).group(1))
            latlonSearch = re.search('lat\s*(-*\d+\.\d+) lon\s*(-*\d+\.\d+)',str.lower(line))
            if latlonSearch:
                latlon.append((latlonSearch.group(1),latlonSearch.group(2)))
            else:
                #print("No long lat!!")
                latlon.append(getLatLong(gridRef[0]))
        if len(gridRef) > 1 :
            # we have site change
            yearSearch = re.search('to\s+\w*\s*([1-2][7-9,0][0-9]{2})',line)
            if yearSearch:
                print(yearSearch.group(1))
            if re.search(gridRef[1],line):
                print(line)
                asml.append(re.search('(\d+)\s*m\w*\samsl',line).group(1))
                latlonSearch = re.search('lat\s*(-*\d+\.\d+) lon\s*(-*\d+\.\d+)',str.lower(line))
                if latlonSearch:
                    latlon.append((latlonSearch.group(1),latlonSearch.group(2)))
                else:
                    #print("No long lat!!")
                    latlon.append(getLatLong(gridRef[0]))
    #print('asml:{}\nlatlon:{}'.format(asml,latlon))

def getLatLong(gridRef):
    import requests
    page = requests.get('http://www.nearby.org.uk/coord.cgi?p='+gridRef+'&f=conv')
    #print(page.text)
    pageSearch = re.search('Decimal: <B>(-*\d+\.\d+) (-*\d+\.\d+)</B>',page.text)
    return (pageSearch.group(1),pageSearch.group(2))
main()