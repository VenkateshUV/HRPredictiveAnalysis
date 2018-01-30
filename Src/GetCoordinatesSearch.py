import pandas as pd

TerminationData = pd.read_csv('HRData/Previous cleaned/MasterData_clean1_Seperated.csv',low_memory=False)
LocationData = pd.read_csv('HRData/LocationALL.csv',low_memory=False)

lat = pd.DataFrame()
lon = pd.DataFrame()
name = pd.DataFrame()

inds = []
for Index, Row in TerminationData.iterrows():
##    print(Index)
    if (Row['Personnel Area - City'] in (LocationData['Personnel Area - City'].values)):
        ind =  LocationData[LocationData['Personnel Area - City'] == Row['Personnel Area - City']].index[0]
        inds.append(ind)
        lat = lat.append(pd.DataFrame([LocationData['Latitude'][ind]],columns = ['Latitude']))
        lon = lon.append(pd.DataFrame([LocationData['Longitude'][ind]],columns = ['Longitude']))
        name = name.append(pd.DataFrame([LocationData['Location Name'][ind]],columns = ['Location Name']))
##        print(locs)
    else:
##        TerminationData['Latitude'].iloc[Index] = 'NAN'
        lat = lat.append(pd.DataFrame(['NAN'],columns = ['Latitude']))
        lon = lon.append(pd.DataFrame(['NAN'],columns = ['Longitude']))
        name = name.append(pd.DataFrame(['NAN'],columns = ['Location Name']))


TerminationData['Latitude'] = lat['Latitude'].values
TerminationData['Longitude'] = lon['Longitude'].values
TerminationData['Location Name'] = name['Location Name'].values
##
##(TerminationData[:,'Latitude'] = pd.Series(LocationData['Latitude'][inds].values, index=TerminationData.index)) if inds!='NAN' else 
##TerminationData[:,'Longitude'] = pd.Series(LocationData['Longitude'][inds].values, index=TerminationData.index)
##TerminationData[:,'Location Name'] = pd.Series(LocationData['Location Name'][inds].values, index=TerminationData.index)
##
TerminationData.to_csv('HRData/MasterData_clean1_loc.csv',encoding='utf-8')
