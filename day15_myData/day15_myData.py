import numpy as np
import pandas as pd
import geopandas as gp
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import requests
import xml.etree.ElementTree as ET
from tqdm import tqdm

import contextily as cx
import xyzservices.providers as xyz

# location of Portsmouth and Val-d'Or
startLoc = (-71.2499, 41.6008)
destLoc_01 = (-77.7968, 48.0987)

# The routing data was obtained following a tutorial by Mandeep Singh on Medium: https://medium.com/walmartglobaltech/finding-and-plotting-optimal-route-using-open-source-api-in-python-cdcda596996c
# ******

start = "{},{}".format(startLoc[0], startLoc[1])
end = "{},{}".format(destLoc_01[0], destLoc_01[1])
# Service - 'route', mode of transportation - 'driving', without alternatives
url = 'http://router.project-osrm.org/route/v1/driving/{};{}?alternatives=false&annotations=nodes'.format(start, end)


headers = { 'Content-type': 'application/json'}
r = requests.get(url, headers = headers)
print("Calling API ...:", r.status_code) # Status Code 200 is success


routejson = r.json()
route_nodes = routejson['routes'][0]['legs'][0]['annotation']['nodes']

route_list = []
for i in range(0, len(route_nodes)):
    if i % 3==1:
        route_list.append(route_nodes[i])

coordinates = []

for node in tqdm(route_list):
    try:
        url = 'https://api.openstreetmap.org/api/0.6/node/' + str(node)
        r = requests.get(url, headers = headers)
        myroot = ET.fromstring(r.text)
        for child in myroot:
            lat, long = child.attrib['lat'], child.attrib['lon']
        coordinates.append((lat, long))
    except:
        continue
print(coordinates[:10])

df_01 = pd.DataFrame({'Node': np.arange(len(coordinates))})
df_01['coordinates'] = coordinates
df_01[['lat', 'long']] = pd.DataFrame(df_01['coordinates'].tolist())

# Converting Latitude and Longitude into float
df_01['lat'] = df_01['lat'].astype(float)

# ******* end of tutorial help

line = LineString(zip(df_01['long'], df_01['lat']))
gdf_01 = gp.GeoDataFrame(index=[0], geometry=[line], crs='EPSG:4326')
gdf_01 = gdf_01.to_crs("EPSG:3857")

startPoint = Point(startLoc)
endPoint = Point(destLoc_01)
# Create a GeoDataFrame with the Point
gdfStart = gp.GeoDataFrame(index=[0], geometry=[startPoint], crs='EPSG:4326')
gdfDest = gp.GeoDataFrame(index=[0], geometry=[endPoint], crs='EPSG:4326')
gdfStart = gdfStart.to_crs(epsg='3857')
gdfDest = gdfDest.to_crs(epsg='3857')


startLoc_3857 = gdfStart.geometry.iloc[0].coords[0]
destLoc_3857 = gdfDest.geometry.iloc[0].coords[0]

minx, miny, maxx, maxy = gdf_01.total_bounds

minxAdj = minx-1.5e5
maxxAdj = maxx+3e5
minyAdj = miny-1.5e5
maxyAdj = maxy+2e5

fig, ax = plt.subplots(figsize=(12, 12)) 

gdf_01.plot(ax=ax, linewidth=2, color='#2B2B67')
gdfStart.plot(ax=ax, color='#2B2B67', marker='o', markersize=100)
gdfDest.plot(ax=ax, color='#2B2B67', marker='o', markersize=100)

fS = 16

ax.annotate(
    "Portsmouth RI", 
    xy=startLoc_3857,  # Coordinates in Web Mercator
    xytext=(startLoc_3857[0] - 1.95e5, startLoc_3857[1] + 0.5e5), 
    arrowprops=dict(facecolor='#2B2B67', arrowstyle="->"),
        fontsize=fS,
    color='#2B2B67',  # Text color
    bbox=dict(
        facecolor='#D6D6EE',  # Background color
        edgecolor='#2B2B67',  # No border
        boxstyle='round,pad=0.5',  # Rounded box with padding
    )
)

ax.annotate(
    "Val-d'Or, QC", 
    xy=destLoc_3857,  # Coordinates in Web Mercator
    xytext=(destLoc_3857[0] + 0.75e5, destLoc_3857[1] + 0.5e5), 
    arrowprops=dict(facecolor='#2B2B67', arrowstyle="->"),
        fontsize=fS,
    color='#2B2B67',  # Text color
    bbox=dict(
        facecolor='#D6D6EE',  # Background color
        edgecolor='#2B2B67',  # No border
        boxstyle='round,pad=0.5',  # Rounded box with padding
    )
)

ax.set_xlim(minxAdj, maxxAdj)
ax.set_ylim(minyAdj, maxyAdj)

# cx.add_basemap(ax=ax, source=cx.providers.OpenStreetMap.Mapnik)
cx.add_basemap(ax=ax, source='https://tile.openstreetmap.org/{z}/{x}/{y}.png', 
	zoom=6)


ax.set_axis_off()
plt.tight_layout()
fig.savefig('aYearOfWalks.png', dpi=300)
plt.show()