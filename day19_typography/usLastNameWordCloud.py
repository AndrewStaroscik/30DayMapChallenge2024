import pandas as pd
import geopandas as gp
from wordcloud import WordCloud
import matplotlib.pyplot as plt

import rasterio
from rasterio.features import geometry_mask

# custom font
fontPath = './data/fonts//Domine-Medium.ttf'

# get the names
names = pd.read_csv('./data/Top1000.csv', skiprows=[0,1, 1003, 1004, 1005, 1006])
names['name'] = names['SURNAME'].apply(lambda x: x.title()) # switch from all caps
names.rename(columns={'FREQUENCY (COUNT)':'count'}, inplace=True)
names['count'] = names['count'].str.replace(',', '').astype(int)

# get the us shape
world = gp.read_file('./data/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp')
us = world[world['ADMIN'] == 'United States of America']
us = us.to_crs(epsg=5070)
targetShape = us.iloc[0].geometry.geoms[0] # get just the lower 48 as a polygon

# the lookup for the word could
nameFreq = dict(zip(names['name'], names['count']))


minx, miny, maxx, maxy = targetShape.bounds
w = 1000
h = 600 # this asymmetry is done to force a look that matches a standard us projection 

# https://rasterio.readthedocs.io/en/latest/api/rasterio.transform.html#rasterio.transform.from_bounds
# takes the polygon and returns a raster of width by height pixels wide. 
transform = rasterio.transform.from_bounds(minx, miny, maxx, maxy, w, h)

# Create the mask
mask = geometry_mask([targetShape], out_shape=(h, w), transform=transform, invert=True)
mask = 255-mask # needed or else cloud is added around the mask

# make the word cloud object
wrdCld = WordCloud(
    font_path=fontPath,
    mask=mask,
    background_color='#FFFDF0',
    contour_width=1,
    min_font_size=1,
    max_words=1000,
    contour_color='#f6f6f6',
    color_func=lambda *args, **kwargs: ('#0016A3'),
    # colormap='Reds',
).generate_from_frequencies(nameFreq)

# create and save the figure
fig, ax = plt.subplots(figsize=(10, 8))

ax.imshow(wrdCld)
ax.set_title('')
ax.set_axis_off()
plt.tight_layout()


fig.text(0.05, 0.95, 'The 1,000 Most Common Last Names in the US', color='#0016A3', fontsize=25)
fig.text(0.025, 0.025, 'Source: US Census Bureau 2010 Census Data', fontsize=9, color='#0016A3')
fig.text(0.7, 0.075, 'Andrew Staroscik', fontsize=20, color='#0016A3')
fig.text(0.705, 0.035, '#30DayMapChallenge', fontsize=15, color='#0016A3')



fig.patch.set_facecolor('#FFFDF0')
fig.savefig('./day19_typography/usLastNameWordCloud.png', dpi=300)


