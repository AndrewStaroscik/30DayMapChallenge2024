
import geopandas as gp
import matplotlib.pyplot as plt

import matplotlib.patches as p

worldMap = gp.read_file('./data/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp')
worldMap = worldMap.set_crs(epsg='4326')

# remove antarctica
worldMapAdj = worldMap[worldMap['ADMIN'] != 'Antarctica']

minx, miny, maxx, maxy = worldMapAdj.total_bounds

missColor = '#dd7878'
onColor = '#175937'

# dynamically create the legned positions based on the scale and projection
meetingXPos = minx + ((maxx - minx) * 0.025)
meetingYPos = miny + ((maxy - miny) * 0.15)
meetingW =( maxx - minx) * 0.05
meetingH = ( maxy - miny) * 0.075

meeting = p.Rectangle((meetingXPos, meetingYPos), meetingW, meetingH, color=onColor)
missing = p.Rectangle((meetingXPos, meetingYPos + meetingH * 1.2), meetingW, meetingH, color=missColor)

fig, ax = plt.subplots(figsize=(10, 5)) 


worldMapAdj.plot(color=missColor, edgecolor='#ffffff', linewidth=0.5, ax=ax)
ax.add_patch(meeting)
ax.text(meetingXPos + meetingW * 1.055, meetingYPos + meetingH/2, 'On Track', verticalalignment='center', fontsize=20, color=onColor)

ax.add_patch(missing)
ax.text(meetingXPos + meetingW * 1.055, meetingYPos + (meetingH * 1.2) + meetingH/2, 'Not On Track', verticalalignment='center', fontsize=20, color=missColor)

ax.set_title('Countries on Track to Meet Paris Climate Accord Targets',fontsize=25, color=missColor, loc='left')

fig.text(0.785, 0.1, 'Andrew Staroscik', fontsize=15, color=missColor)
fig.text(0.794, 0.07, '#30DayMapChallenge', fontsize=10, color=missColor)

ax.set_axis_off()
plt.tight_layout()

fig.savefig('./day22_twoColors/climateTarget.png', dpi=300)
