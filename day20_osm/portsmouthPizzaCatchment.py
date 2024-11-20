import osmnx as ox
import geopandas as gp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.patches as patches

from shapely.geometry import Polygon

from scipy.spatial import Voronoi

import contextily as cx
import xyzservices.providers as xyz
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


# get restaurants from OSM
place_name = "Portsmouth, Rhode Island, USA"
tags = {"amenity": "restaurant"}

pois = ox.features.features_from_place(place_name, tags)

# limit to pizza only
pizza = pois[pois['cuisine'].isin(['pizza', 'Pizza'])]


# get town map 
riMun = gp.read_file('./data/Municipalities_(1997)/Municipalities__1997_.shp')
ports = riMun[riMun['NAME'] == 'PORTSMOUTH']
ports = ports.sort_values(by='SHAPE_Area', ascending=False)

# use only the main shape, exclude Prudence Island and other smaller features
ports = gp.GeoSeries(ports.iloc[0].geometry)

# make sure ports is a GeoDataFrame
ports = ports.to_frame(name="geometry")

# make the voronoi pattern
points = np.array([(point.x, point.y) for point in pizza.geometry])

minx, miny, maxx, maxy = ports.total_bounds
areaAdj = 3  
boundingPoints = [
    (minx - areaAdj, miny - areaAdj),  
    (minx - areaAdj, maxy + areaAdj),  
    (maxx + areaAdj, miny - areaAdj),  
    (maxx + areaAdj, maxy + areaAdj)   
]

allPoints = [(point.x, point.y) for point in pizza.geometry] + boundingPoints

vor = Voronoi(allPoints)

voronoiPolys = []
for region in vor.regions:
    if not -1 in region and len(region) > 0: 
        polygon = Polygon([vor.vertices[i] for i in region])
        if polygon.is_valid and polygon.area > 0:
            voronoiPolys.append(polygon)
            
voronoiGDF = gp.GeoDataFrame(geometry=voronoiPolys, crs=ports.crs)

maskedVor = gp.clip(voronoiGDF, ports)

# use custom marker for pizza places
def add_custom_marker(ax, x, y, image_path):
    img = plt.imread(image_path)  
    imagebox = OffsetImage(img, zoom=0.175)  
    ab = AnnotationBbox(imagebox, (x, y), frameon=False)
    ax.add_artist(ab)

    # make sure all crs's match
pizza_3857 = pizza.to_crs(epsg=3857)
ports.set_crs(epsg=4326, inplace=True)
ports_3857 = ports.to_crs(epsg=3857)
maskedVor.set_crs(epsg=4326, inplace=True)
maskedVor_3857 = maskedVor.to_crs(epsg=3857)

# recalculate after crs change
minx, miny, maxx, maxy = ports_3857.total_bounds

adj = 5e3
yadj = 0.25

minxAdj = minx-adj
maxxAdj = maxx+adj
minyAdj = miny-adj * yadj
maxyAdj = maxy+adj * yadj


fig, ax = plt.subplots(figsize=(10, 12)) 




ax.set_xlim(minxAdj, maxxAdj)
ax.set_ylim(minyAdj, maxyAdj)


maskedVor_3857.plot(color='none', edgecolor='#FF8D0A', linewidth=2,ax=ax)
ports_3857.plot(ax=ax, color='none', edgecolor='#DDBBBB', linewidth=0.2)


for x, y in zip(pizza_3857.geometry.x, pizza_3857.geometry.y):
    add_custom_marker(ax, x, y, './data/pizzaIcon.png')  

rect = patches.Rectangle((minxAdj, minyAdj), maxxAdj - minxAdj,  maxyAdj - minyAdj,  linewidth=2,   edgecolor='#454545',  facecolor='none')


ax.add_patch(rect)

# Add a one mile scale bar
scale_bar_length_meters = 8046.72 / 5 # given projection (3857) the units here are meters
scale_bar_start_x = ports_3857.total_bounds[0] - 0.35 * (ports_3857.total_bounds[2] - ports_3857.total_bounds[0])
scale_bar_start_y = ports_3857.total_bounds[1] + 0.05 * (ports_3857.total_bounds[3] - ports_3857.total_bounds[1])


ax.hlines(y=scale_bar_start_y, xmin=scale_bar_start_x, xmax=scale_bar_start_x + scale_bar_length_meters, color='black', linewidth=3)
ax.text(scale_bar_start_x + scale_bar_length_meters / 2, scale_bar_start_y - 500, '1 mi', horizontalalignment='center', fontsize=15, color='black')

cx.add_basemap(ax=ax, source=cx.providers.CartoDB.PositronNoLabels)

ax.set_title('Portsmouth Pizza Restaurant Catchment Basins',fontsize=18, color='#454545', loc='left')
fig.text(0.11, 0.065, 'Data Source: OpenStreetMap', fontsize=9, color='#565656')
fig.text(0.785, 0.0675, 'Andrew Staroscik', fontsize=15, color='#565656')
fig.text(0.79, 0.055, '#30DayMapChallenge', fontsize=10, color='#565656')
plt.tight_layout()

ax.set_axis_off()
fig.savefig('./day20_osm/portsmouthPizzaCatchment.png', dpi=300)

