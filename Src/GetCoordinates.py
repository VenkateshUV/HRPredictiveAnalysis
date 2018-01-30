import pandas as pd
from geopy.geocoders import Nominatim
geolocator = Nominatim()

TerminationData = pd.read_csv('HRData/UNCC_Termination UNION_beforeLoc.csv',low_memory=False)
LocationData = pd.read_csv('LocationALL.csv',low_memory=False)
#location = []
lat = []
long = []
Word = []


for Index, Row in LocationData.iterrows():
    Address = Row['Personnel Area - City']+' '+Row['Personnel Area - State']+' '+Row['Personnel Area - Country']
    #lat, lng = gmaps.address_to_latlng(address)
    print(Address)
    location = (geolocator.geocode(Address))
    lat.append(location[1][0])
    long.append(location[1][1])
    Word.append(location[0])
    
LocationData['Latitude'] = pd.DataFrame(lat,columns = ['Latitude'])
LocationData['Longitude'] = pd.DataFrame(long,columns = ['Longitude'])
LocationData['Location Name'] = pd.DataFrame(Word,columns = ['Location Name'])
    
LocationData.to_csv('LocationSecond.csv')



inds = []
for Index, Row in TerminationData.iterrows():
    ind =  LocationData[LocationData['Personnel Area - City'] == Row['Personnel Area - City']].index[0]
    inds.append(ind)

TerminationData['Latitude'] = pd.DataFrame(inds,columns = [LocationData['Latitude'][inds.tolist()]])
TerminationData['Longitude'] = pd.DataFrame(inds,columns = [LocationData['Longitude'][inds.tolist()]])
