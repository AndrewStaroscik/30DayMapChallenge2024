import pandas as pd
import geopandas as gp
import matplotlib.pyplot as plt
from shapely.geometry import Point

import numpy as np

# population data source: https://population.un.org/wpp/Download/Standard/CSV/
pop = pd.read_csv('./data/WPP2024_PopulationByAge5GroupSex_Medium.csv')
subset = pop[(pop['LocTypeName'] == 'Country/Area') & (pop['Time'] == 2024)]
popEst = subset.groupby('Location', as_index=False)['PopTotal'].sum()
popEst['ADMIN'] = popEst['Location']

# land area data: https://data.worldbank.org/indicator/AG.SRF.TOTL.K2
land = pd.read_csv('./data/API_AG.SRF.TOTL.K2_DS2_en_csv_v2_9771.csv', skiprows=[0,1,2,3])

areaOptions = [
    ~land['2023'].isna(),
    ~land['2022'].isna(),
    ~land['2021'].isna(),
    ~land['2020'].isna(),
    ~land['2019'].isna(),
    ~land['2018'].isna(),
]
order = [land['2023'], land['2022'],land['2021'],land['2020'],land['2019'],land['2018']]

land['area'] = np.select(areaOptions, order, default=np.nan)
land['ADMIN'] = land['Country Name']
land['ADM0_A3'] = land['Country Code']
land = land[['ADMIN', 'ADM0_A3', 'area']]

# use this base map to get the center location of all countries
baseMap = gp.read_file('./data/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp')
base_3857 = baseMap.to_crs(epsg='3857')
countryCenters = base_3857.geometry.centroid
centers_3857 = gp.GeoDataFrame(base_3857.drop(columns='geometry'), geometry=countryCenters, crs=base_3857.crs)

# add data
centers_3857 = centers_3857.merge(popEst[['ADMIN', 'PopTotal']], on='ADMIN', how='left')
centers_3857 = centers_3857.merge(land[['ADM0_A3', 'area']], on='ADM0_A3', how='left')

# manually add area for antarctica
centers_3857.loc[centers_3857['ADMIN'] == 'Antarctica', 'area'] = 14.2e6

# drop rows lacking area data
centers_3857= centers_3857[~centers_3857['area'].isna()]


# make circle shapes as geometry
popMap = centers_3857.copy()
popMap['geometry'] = centers_3857['geometry'].buffer(centers_3857['PopTotal']*2, resolution=10)
popMap = popMap.to_crs(epsg='4326')

areaMap = centers_3857.copy()
areaMap['geometry'] = centers_3857['geometry'].buffer(centers_3857['area']/10, resolution=10)
areaMap = areaMap.to_crs(epsg='4326')

# save new geometries
popMap.to_file('./day24_circles/countryPops.json', driver='GeoJSON')
areaMap.to_file('./day24_circles/countryAreas.json', driver='GeoJSON')
