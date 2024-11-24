import geopandas as gp
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.font_manager import FontProperties





import urllib.request, urllib.error, urllib.parse, json
import lxml

ak = '<enter a acs api key heregit ad'

states = gp.read_file('./data/usInsetMap/usInsetMap.shp') # this is a Alberts projection that I made with AK and HI placed in "insets" below the lower 48
minx, miny, maxx, maxy = states.total_bounds
maxx = -67 # fix for issues with AK extending the x axis around the globe

alzPrev = pd.read_csv('./data/alzPrev20_25.csv')
alzPrev['NAME'] = alzPrev['State'] # makes merge easier

states = states.merge(alzPrev[['NAME', '2020', '2025', '2020-2025']], on='NAME', how='left')

# get census data
urlSt = 'https://api.census.gov/data/2023/acs/acs1?get=NAME,B01001_001E,B01001_002E,B01001_020E,B01001_021E,B01001_022E,B01001_023E,B01001_024E,B01001_025E,B01001_026E,B01001_044E,B01001_045E,B01001_046E,B01001_047E,B01001_048E,B01001_049E&for=state:*&key=' + ak

response = urllib.request.urlopen(urlSt) 
data = response.read().decode('UTF-8')
data = json.loads(data) 
pop = pd.DataFrame(data[1:], columns=data[0])

pop['65+'] = pop[['B01001_020E', 'B01001_021E', 'B01001_022E', 'B01001_023E', 'B01001_024E', 'B01001_025E', 'B01001_044E', 'B01001_045E', 'B01001_046E', 'B01001_047E', 'B01001_048E', 'B01001_049E']].astype(int).sum(axis=1)

pop['pct65+'] = 100 * pop['65+'] / pop['B01001_001E'].astype(int)

states = states.merge(pop[['NAME', '65+']], on='NAME', how='left')


states['pct65plus'] =  round(100 * states['2025'] / (states['65+'] / 1e3),2)

states['per1k65plus'] = states['2025'] / (states['65+'] / 1e3)

lowVal = 0
highVal = 15
midVal = 10
midProp = (midVal-lowVal)/(highVal-lowVal)

legendFont = FontProperties(family='Roboto Slab', size=14, weight='regular')
titleFont = FontProperties(family='Roboto', size=19, weight='light')

colors = [(0.0, '#CCFFD3'), (midProp, '#FFEB99'), (1.0, '#C90B00')] 
customMap = LinearSegmentedColormap.from_list("custom_cmap", colors)

norm = Normalize(vmin=lowVal, vmax=highVal)

# fig, ax = plt.subplots(figsize=(12.8, 7.2))
fig, ax = plt.subplots(figsize=(10, 7.2))


ymargin = 0.00001
xmargin = 0.0001
plt.subplots_adjust(left=xmargin, right=1-xmargin, bottom=ymargin, top=0.9)


ax.set_xlim(minx-1, maxx+1)
ax.set_ylim(miny-1, maxy+1)


states.plot(
    ax=ax, cmap=customMap, norm=norm, column='pct65plus', edgecolor='#ffffff', linewidth=0.5, legend=True,
    legend_kwds={
        'shrink': 0.45,
        'anchor': (0.5, 2.25),
        'orientation': 'horizontal',
        'label': '!!!'
    }
)

cbar = ax.get_figure().axes[-1] 
cbar.set_xlabel('Incidence per 100,000 individuals aged 65 and older',fontsize=legendFont.get_size(),fontname=legendFont.get_name())


fig.text( 0.1, 0.92, "Alzheimer's Disease in Elderly Population", fontsize=titleFont.get_size(), fontname=titleFont.get_name(), fontweight='bold', color='#7C0700')
fig.text( 0.44, 0.885, '(2025 Estimate)', fontsize=titleFont.get_size()-4, fontname=titleFont.get_name(), fontweight='bold', color='#7C0700')
fig.text(0.08, 0.125, "Data: Alzheimer's Association and US Census Bureau", fontsize=8, fontname=legendFont.get_name(), color='#565656')
fig.text(0.8, 0.135, 'Andrew Staroscik', fontsize=12, fontname=legendFont.get_name(), horizontalalignment='center', color='#898989')
fig.text(0.8, 0.11, '#30DayMapChallenge', fontsize=9, fontname=legendFont.get_name(), horizontalalignment='center', color='#898989')


ax.set_axis_off()
fig.savefig('./day23_memory/alzPrev2025.png', dpi=150)

