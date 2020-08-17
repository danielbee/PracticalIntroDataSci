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
        stationFrame = getDataFrame(stationDataRaw[station])
        # Extract things like height above sea level, longitude and latitude and site changes.
        stationFrame = getDataExtras(stationDataRaw[station],stationFrame)
        # add a column for the station
        stationFrame['station'] = station
        # Make station column the most signifiant index in the multiIndex
        stationFrame.set_index(['station', stationFrame.index],inplace=True)
        # Append to list of dataframes
        bigFrame.append(stationFrame)
    # Combine all the dataframes
    stationsData = pd.concat(bigFrame)
   # print(stationsData.reset_index().dtypes)
    # Print out in desired formats
    stationsData.to_excel(dataPath+'stationData.xlsx')
    stationsData.to_csv(dataPath+'stationData.csv')
    
    stationsData.to_string(dataPath+'stationData.txt')

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
        if record['yyyy'] != None:
            records.append(record)
    
    df = pd.DataFrame.from_dict(records)
    df[['yyyy','mm']] = df[['yyyy','mm']].astype(int)
    # other columns
    df[['tmax','tmin','af','rain','sun']] = df[['tmax','tmin','af','rain','sun']].astype(float)
    df.set_index(['yyyy', 'mm'],inplace=True)
    #print(df)
    return df
    
import math
def getDataExtras(raw,df):
    topRaw = '\n'.join(raw[0:20])

    gridRef = re.findall(r'\d+E \d+N',topRaw)
    asml=[]
    latlon=[]
    lowerYr=[]
    upperYrMonth=[]
    upperYr=[]
    ## Extract Features
    for line in raw[0:20]:
        if re.search(gridRef[0],line):
            print(line)
            if len(gridRef) > 1 : 
                yearSearch = re.search(r'([1-2][7-9,0][0-9]{2})?\s+(\bfrom\b|\bafter\b|\bto\b|\buntil\b)\s+([a-zA-Z]*)\s*([1-2][7-9,0][0-9]{2})',line)
                #print(yearSearch)
                if yearSearch:
                    lowerYr.append(yearSearch.group(1))
                    upperYrMonth.append(yearSearch.group(3))
                    upperYr.append(yearSearch.group(4))
                    print('from {} to {} {}'.format(lowerYr[0],upperYrMonth[0],upperYr[0]))

            asml.append(re.search(r'(\d+)\s*m\w*\samsl',line).group(1))
            latlonSearch = re.search(r'lat\s*(-*\d+\.\d+) lon\s*(-*\d+\.\d+)',str.lower(line))
            if latlonSearch:
                latlon.append((latlonSearch.group(1),latlonSearch.group(2)))
            else:
                #print("No long lat!!")
                latlon.append(getLatLong(gridRef[0]))
        if len(gridRef) > 1 :
            # we have site change
            if re.search(gridRef[1],line):
                print(line)
                yearSearch = re.search(r'([1-2][7-9,0][0-9]{2})?\s+(\bfrom\b|\bafter\b|\bto\b)\s+([a-zA-Z]*)\s*([1-2][7-9,0][0-9]{2})',line)
                #print(yearSearch)
                if yearSearch:
                        lowerYr.append(yearSearch.group(1))
                        upperYrMonth.append(yearSearch.group(3))
                        upperYr.append(yearSearch.group(4))
                        print('from {} to {} {}'.format(lowerYr[-1],upperYrMonth[-1],upperYr[-1]))
                asml.append(re.search(r'(\d+)\s*m\w*\samsl',line).group(1))
                latlonSearch = re.search(r'lat\s*(-*\d+\.\d+) lon\s*(-*\d+\.\d+)',str.lower(line))
                if latlonSearch:
                    latlon.append((latlonSearch.group(1),latlonSearch.group(2)))
                else:
                    #print("No long lat!!")
                    latlon.append(getLatLong(gridRef[0]))
    #print('asml:{}\nlatlon:{}'.format(asml,latlon))
    ## Add features to dataframe

    # This is wrong, but i just want to get data in there and start classify.
    # Tehcnically, we should determine site changes , which may have a significant impact on frost days if asml gets higher.  
    extra_df = setExtrasInDf(df,
                        df_filter= df.index.get_level_values('yyyy') > 0,
                        asml=asml[0], lat=latlon[0][0],long=latlon[0][1],gridRef=gridRef[0]
                    )
    
    with open('dfL.txt','a') as f:
        print(extra_df.to_string(), file=f)
    return extra_df
    if len(gridRef) >1:
        # Need to apply features using extracted years. 
        #print(df.dtypes)
        tempTypeDf = df.reset_index()
        #tempTypeDf[['yyyy','mm']] = tempTypeDf[['yyyy','mm']].astype(int)
        #tempTypeDf[['tmax','tmin','af','rain','sun']] = tempTypeDf[['tmax','tmin','af','rain','sun']].astype(float)
        #defensive
        if len(lowerYr) >0 and len(upperYr) >0:
            # We were able to find SOMETHING we can use.
            print('lower: {} \t upper: {} \t month {}'.format(lowerYr,upperYr,upperYrMonth))
            #if upperYr[0] > lowerYr[1]: 
            #    print('issue')
            if len(lowerYr) == 1:
                # super simple
                #if upperYrMonth[0]:
                #    
                #    tempTypeDf = setExtrasInDf(tempTypeDf,
                #        df_filter= tempTypeDf['yyyy']<int(upperYr[0]) or (tempTypeDf['yyyy']==int(upperYr[0]) and tempTypeDf['mm']<int(upperYrMonth[0])),
                #        asml=asml[0], lat=latlon[0][0],long=latlon[0][1],gridRef=gridRef[0]
                #    )
                #   tempTypeDf = setExtrasInDf(tempTypeDf,
                #       df_filter= tempTypeDf['yyyy']>=int(upperYr[0]) or (tempTypeDf['yyyy']==int(upperYr[0]) and tempTypeDf['mm']>=int(upperYrMonth[0])),
                #       asml=asml[1], lat=latlon[1][0],long=latlon[1][1],gridRef=gridRef[1]
                #   )
                #else:
                    tempTypeDf = setExtrasInDf(tempTypeDf,
                        df_filter= tempTypeDf['yyyy']<int(upperYr[0]),
                        asml=asml[0], lat=latlon[0][0],long=latlon[0][1],gridRef=gridRef[0]
                    )

                    tempTypeDf = setExtrasInDf(tempTypeDf,
                        df_filter=tempTypeDf['yyyy']>=int(upperYr[0]),
                        asml=asml[1], lat=latlon[1][0],long=latlon[1][1],gridRef=gridRef[1]
                    )
                    #if lowerYr[0] and upperYr[0]:
                    #    tempTypeDf = setExtrasInDf(tempTypeDf,
                    #        df_filter= tempTypeDf['yyyy']>=int(lowerYr[0]) and tempTypeDf['yyyy']<int(upperYr[0]),
                    #        asml=asml[0], lat=latlon[0][0],long=latlon[0][1],gridRef=gridRef[0]
                    #    )
                    #    tempTypeDf = setExtrasInDf(tempTypeDf,
                    #        df_filter= tempTypeDf['yyyy']>=int(upperYr[0]),
                    #        asml=asml[1], lat=latlon[1][0],long=latlon[1][1],gridRef=gridRef[1]
                    #    )
                    #elif upperYr[0] and lowerYr[0] == None:
                        

            #if lowerYr[0] == None and lowerYr[1] == None:
            #    if upperYr[0] and upperYr[1]:
            #        # Nice simple case
            #        if upperYr[0] == upperYr[1]:
            #            tempTypeDf = setExtrasInDf(tempTypeDf,
            #                df_filter= tempTypeDf['yyyy']<int(upperYr[1]),
            #                asml=asml[0], lat=latlon[0][0],long=latlon[0][1],gridRef=gridRef[0]
            #            )
            #            tempTypeDf = setExtrasInDf(tempTypeDf,
            #                df_filter= tempTypeDf['yyyy']>=int(upperYr[1]),
            #                asml=asml[0], lat=latlon[0][0],long=latlon[0][1],gridRef=gridRef[0]
            #            )
                    ## TODO: 
                    #if upperYrMonth[0] and upperYrMonth[1] :
#
                    #elif upperYrMonth[0] and upperYrMonth[1] == None:
                    #elif upperYrMonth[1]:
                    #else:
        else : 
            print('unable to aquire site change year. Will dump other grid refs of {} and keep only {}.'.format(gridRef[1:],gridRef[0]))
        if len(upperYr) >0 :
            #tempTypeDf = setExtrasInDf(
            #    tempTypeDf,
            #    df_filter= tempTypeDf['yyyy']<int(upperYr[-1]),
            #    asml=asml[0], lat=latlon[0][0],long=latlon[0][1],gridRef=gridRef[0])
            #tempTypeDf = setExtrasInDf(
            #    tempTypeDf,
            #    df_filter= tempTypeDf['yyyy']>=int(upperYr[-1]),
            #    asml=asml[-1], lat=latlon[-1][0],long=latlon[-1][1],gridRef=gridRef[-1])
            #tempTypeDf.loc[tempTypeDf['yyyy']<int(upperYr[-1]),'asml'] = int(asml[0])
            #tempTypeDf.loc[tempTypeDf['yyyy']<int(upperYr[-1]),'Lat'] = float(latlon[0][0])
            #tempTypeDf.loc[tempTypeDf['yyyy']<int(upperYr[-1]),'Long'] = float(latlon[0][1])
            #tempTypeDf.loc[tempTypeDf['yyyy']>=int(upperYr[-1]),'asml'] = int(asml[-1])
            #tempTypeDf.loc[tempTypeDf['yyyy']>=int(upperYr[-1]),'Lat'] = float(latlon[-1][0])
            #tempTypeDf.loc[tempTypeDf['yyyy']>=int(upperYr[-1]),'Long'] = float(latlon[-1][1])
            #print(len(tempTypeDf.reset_index()['yyyy']))            
            #print(len([int(x) for x in tempTypeDf.index.get_level_values('yyyy').values if (math.isnan(float(x)) == False)]))
            with open('df.txt','a') as f:
                print(tempTypeDf.to_string(), file=f)
            #    print(tempTypeDf.reset_index().dropna(subset=['yyyy']).to_string(), file=f)
            #with open('df_before.txt','w') as f:
            #    print(tempTypeDf.reset_index().to_string(), file=f)
            #.loc[:(upperYr[-1],),:])
            #print([int(x) for x in tempTypeDf.index.get_level_values('yyyy').values if (math.isnan(float(x)) == False and x == upperYr[-1])])
            #print([int(x) for x in tempTypeDf.index.get_level_values('yyyy').values if (math.isnan(float(x)) == False and x != upperYr[-1])])

def setExtrasInDf(df, df_filter, asml, lat, long, gridRef): 
    df.loc[df_filter,'asml'] = int(asml)
    df.loc[df_filter,'lat'] = float(lat)
    df.loc[df_filter,'long'] = float(long)
    df.loc[df_filter,'gridRef'] = str(gridRef)
    return df
def getLatLong(gridRef):
    import requests
    page = requests.get('http://www.nearby.org.uk/coord.cgi?p='+gridRef+'&f=conv')
    #print(page.text)
    pageSearch = re.search(r'Decimal: <B>(-*\d+\.\d+) (-*\d+\.\d+)</B>',page.text)
    return (pageSearch.group(1),pageSearch.group(2))
main()