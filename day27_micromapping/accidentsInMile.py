import pandas as pd
import geopandas as gp
from shapely.geometry import box, Point

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

import contextily as cx
import xyzservices.providers as xyz

# this takes a point and returns a four sided polygon enclosing a square mile around the point
def makesSqMi(p):
  halfMi = 1609.34/2
  pointLat = p.geometry.y 
  pointLon = p.geometry.x 
  targetArea = box(pointLon - halfMi, pointLat - halfMi, pointLon + halfMi, pointLat + halfMi)
  tmpGDF = gp.GeoDataFrame([p.drop('geometry')], geometry=[targetArea], crs="EPSG:2163")
  return tmpGDF

accidentPopTargetCols = ['STATE', 'ST_CASE', 'COUNTY', 'LATITUDE', 'LONGITUD', 'HARM_EV', 'TYP_INT', 'LGT_COND', 'FATALS', 'MONTH', 'MONTHNAME', 'DAY', 'DAYNAME', 'DAY_WEEK', 'DAY_WEEKNAME', 'YEAR', 'HOUR', 'HOURNAME', 'MINUTE', 'MINUTENAME']
data = pd.read_csv('./data/accident.csv', encoding='utf-8', encoding_errors='ignore', usecols=accidentPopTargetCols, dtype={'STATE': str, 'COUNTY': str})

# create the geometry for mapping: 
geometry = [Point(xy) for xy in zip(data['LONGITUD'], data['LATITUDE'])]
data = gp.GeoDataFrame(data, geometry=geometry)
data.set_crs(epsg=4326, inplace=True)
data = data.to_crs(epsg=2163) # an equal area projection for mapping the US. Use to calculate square miles

# list to capture counts of accidents within 1mi^2 of each accident. 
localEvents = []

for i, pt in data.iterrows():  
  
  tmpAreaGF = makesSqMi(pt)
  tmpArea = tmpAreaGF.geometry.iloc[0]
  if tmpArea.is_valid:  
  	tmpAccidentList = data[data.intersects(tmpArea)]
  else: 
    tmpAccidentCount = 0 # deal with missing geolocations
  localEvents.append({'index': i, 'accidentsInArea': tmpAccidentList, 'sqArea':tmpAreaGF, 'count': len(tmpAccidentList)})

# this was found by trial and error. Will change with different year or area search size. 
mostAccidents = [el for el in localEvents if el['count'] == 11]
mostAccidentsIndexes = [el['index'] for el in mostAccidents]
topAreas = data[data.index.isin(mostAccidentsIndexes)]

# This showed that they are in the same small area
# topAreas.plot()

# Since sll three >11 hits are the in the same area of Atlanta, I Will use the middle one for the map. 
# Either of the other two would work just as well.
targetSqMile = mostAccidents[1]

topAreas.to_crs(epsg=3857, inplace=True) # use this to set x and y lim of map

minx, miny, maxx, maxy = topAreas.total_bounds
extent = (minx, maxx, miny, maxy)

minxAdj = minx-1e4
maxxAdj = maxx+1e4
minyAdj = miny-1e4
maxyAdj = maxy+1e4 

xLegend, yLegend = 0.7, 0.75


fig, ax = plt.subplots(figsize=(12, 12)) 


ax.set_xlim(minxAdj, maxxAdj)
ax.set_ylim(minyAdj, maxyAdj)

# all local accidents
data[data['STATE'] == '13'].to_crs(epsg=3857).plot(
  ax=ax, 
  markersize=25, 
  color='#FFA72B', 
  edgecolor='#EA8900', 
  linewidth=1
)

# box around the target square mile
targetSqMile['sqArea'].to_crs(epsg=3857).plot(
  ax=ax, 
  color='none', 
  edgecolor='red', 
  linewidth=2
)

# accidents in the target square mile
targetSqMile['accidentsInArea'].to_crs(epsg=3857).plot(
  ax=ax, 
  markersize=30, 
  color='#FF6D89', 
  edgecolor='#FF2D55', 
  linewidth=1
)

# base map
cx.add_basemap(ax=ax, alpha=0.4, source=cx.providers.USGS.USTopo)

# box around the legend (upper right)
bbox = FancyBboxPatch(
    (xLegend, yLegend),
    0.175, 0.055,            
    boxstyle="round,pad=0.009", 
    edgecolor="black",
    facecolor="white",
    transform=fig.transFigure, 
    zorder=2,
)
ax.add_patch(bbox)

# box around the information (lower left)
bbox = FancyBboxPatch(
    (0.145, 0.25),
    0.29, 0.07,            
    boxstyle="round,pad=0.009",  
    edgecolor='white',
    facecolor='white',
    alpha=0.75,
    transform=fig.transFigure,  
)
ax.add_patch(bbox)

circle = Circle(
    (xLegend + 0.015, yLegend + 0.04), 
    0.0075,                               
		color='#FF6D89', ec='#FF2D55', linewidth=1,
    transform=fig.transFigure,
    zorder=3,  
)
fig.patches.append(circle)

fig.text(
    xLegend + 0.028, yLegend + 0.04,  
    'Accidents in Square Mile',      
    color='#6D0015',
    va='center',    
    fontsize=10,
    zorder=3
)

circle = Circle(
    (xLegend + 0.015, yLegend + 0.015),  
    0.005,                               
		color='#FFA72B', ec='#EA8900', linewidth=1,
    transform=fig.transFigure,
    zorder=3,  
)
fig.patches.append(circle)

fig.text(
    xLegend + 0.025, yLegend + 0.015,  
    'Other Fatal Accidents',      
    color='#6A3E00',
    va='center',    
    fontsize=10,
    zorder=3
)

ax.set_title('One of the Most Dangerous Square Miles in the US',fontsize=20, color='#454545', loc='left')
fig.text( 0.15, 0.25, 'This one square mile in Atlanta,\nGeorgia had more fatal traffic\naccidents in 2022 than any other\nplace in the U.S.', fontsize=15, color='#6D0015')
fig.text(0.125, 0.135, 'Data: NHTSA Fatality Analysis Reporting System' , fontsize=9, color='#232323')
fig.text(0.8, 0.135, 'Andrew Staroscik', fontsize=12, horizontalalignment='center', color='#232323')
fig.text(0.8, 0.12, '#30DayMapChallenge', fontsize=9, horizontalalignment='center', color='#232323')
ax.set_axis_off()
fig.savefig('./day27_micromapping/oneSqMile.png', dpi=300)

