
import geopandas as gp
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.font_manager import FontProperties

states = gp.read_file('./data/usInsetMap/usInsetMap.shp') # this is a Alberts projection that I made with AK and HI placed in "insets" below the lower 48

hurTor = pd.read_csv('./data/hurricane_tornado_last12mo.csv')
hurTor['idx'] = hurTor['hurricane']*2-1
hurTor['NAME'] = hurTor['State']

states = states.merge(hurTor[['NAME', 'idx']], on='NAME', how='left')

# Custom colormap
colors = [(0.0, '#FF8D0A'),(0.5, '#FCFFA3'), (1.0, '#0A7CFF')]
custom_cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)
norm = Normalize(vmin=-1, vmax=1) 


minx, miny, maxx, maxy = states.total_bounds

titleFont = FontProperties(family='Domine', size=16, weight='light')
legendFont = FontProperties(family='Roboto', size=14, weight='regular')
sourceTextFont = FontProperties(family='Roboto', size=9, weight='regular')
nameTextFont = FontProperties(family='Roboto', size=15, weight='regular')
challengeTextFont = FontProperties(family='Roboto', size=10, weight='regular')

maxx = -67 # fix for issues with AK extending the x axis around the globe
fig, ax = plt.subplots(figsize=(10, 7)) 

ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy + 3)
ax.set_axis_off()
plt.tight_layout()

states.plot(ax=ax, cmap=custom_cmap, column='idx', norm=norm, edgecolor='#676767', linewidth=0.15, legend=True, legend_kwds={'shrink': 0.45, 'anchor':(0.5, 2.25), 'orientation': 'horizontal'})

cbar = ax.get_figure().axes[-1] 
cbar.set_yticklabels([]) 
cbar.tick_params(bottom=False, right=False, labelbottom=False, labelright=False)

cbar_ax = ax.get_figure().axes[-1]
cbar_ax.tick_params(axis='x', labelrotation=0) 
cbar.set_xlabel('<-- More Tornado                  More Hurricane  -->', fontsize=legendFont.get_size(), labelpad=10, fontname=legendFont.get_name(), fontweight=legendFont.get_weight(), color='#666')

fig.text( 0.15, .95, 'Google Search Trends Hurricane vs Tornado (Nov 23 - Nov 24)', fontsize=titleFont.get_size(), fontweight=titleFont.get_weight(), fontname=titleFont.get_name(), color= '#454567')
fig.text( 0.15, 0.25, 'Data Source: Google', fontsize=sourceTextFont.get_size(), fontname=sourceTextFont.get_name(), weight=sourceTextFont.get_weight(), color='#444444')
fig.text(0.75, 0.26, 'Andrew Staroscik',fontsize=nameTextFont.get_size(), fontname=nameTextFont.get_name(),  weight=nameTextFont.get_weight(), color='#666666')
fig.text( 0.76, 0.23, '#30DayMapChallenge', fontsize=challengeTextFont.get_size(), fontname=challengeTextFont.get_name(), weight=challengeTextFont.get_weight(), color='#676767')

ax.set_axis_off()
plt.tight_layout()
fig.savefig('./day21_conflict/hurricaneVsTornado.png', dpi=300)

