import folium
import pandas as pd
import geopandas as gp
from branca.element import Figure
from folium import Element
import branca

# get data
world = gp.read_file('../data/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp')
re = pd.read_csv('../data/renewPct2023.csv',encoding='latin-1', dtype={'pct_re': float})
world = world.merge(re[['ADMIN', 'pct_re']], on='ADMIN', how='left')
# Drop rows where pct_re is NaN
world = world[~world['pct_re'].isna()]

fig = Figure(width='100%', height='100%')

m = folium.Map(location=[20, 0], zoom_start=3, tiles='cartodb positron')
fig.add_child(m)


colormap = branca.colormap.LinearColormap(
    colors=['#FEF9D1', '#86FCA1', '#86B9FC'],  
    vmin=world['pct_re'].min(),
    vmax=world['pct_re'].max(),
    caption='Renewable Energy (%)'
)

colormap.tick_labels = [0, 50, 100]

colormap.add_to(m)


# add border around legend to make it easier to read
custom_css = """
<style>
    div.leaflet-control {
        padding: 12px 5px 5px 5px;
        background-color: rgba(255, 255, 255, 0.9);
        border: 2px solid grey;
        border-radius: 8px;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
        font-size:15px;
    }
    #legend .tick text{
        font-size: 12px !important;
    }
    #legend .caption text{
        font-size: 18px !important;
    }
</style>
"""
m.get_root().html.add_child(Element(custom_css))

geojson = folium.GeoJson(
    data=world.__geo_interface__,
 		style_function=lambda feature: {
    	'fillColor': colormap(feature['properties'].get('pct_re')),
    	'color': '#676767',
    	'weight': 0.5,
    	'fillOpacity': 1
		},
    tooltip=folium.features.GeoJsonTooltip(
        fields=['ADMIN', 'pct_re'],
        aliases=['Country: ', 'Renewables (%)'],
        localize=True,
        style=('font-size:15px; border-radius:10px;')
    )
).add_to(m)

# Add Title and annotations
html = """
<div style='position: fixed; 
  top: 10px; 
  left: 100px; 
  padding: 10px; 
  background: #efefef;
  border-radius: 10px; 
  z-index:9999; 
  font-size:20px;'>
    <p>
        <b>2023 Renewable Energy Consumption by Country (% of total)</b>
    </p>
</div>
"""

sourceCredit = """
<div style='position: fixed; 
  bottom: 5px; 
  left: 10px; 
  color: #232323;
  z-index:1000; 
  font-size:15px;'>
    <p>
        <a href='https://pxweb.irena.org/pxweb/en/IRENASTAT/'>Source: International Renewable Energy Agency</a>
    </p>
</div>
"""

acknowl = """
<div style='position: fixed; 
  bottom: 30px; 
  right: 10px; 
  color: #232323;
  z-index:1000; 
  font-size:15px;
  text-align: center;'>
    <p> <b><span style='font-size:1.2em'>
       Andrew Staroscik </span></b><br />
			#30DayMapChallenge</p>
</div>
"""

m.get_root().html.add_child(Element(html))
m.get_root().html.add_child(Element(acknowl))
m.get_root().html.add_child(Element(sourceCredit))

folium.LayerControl().add_to(m) # this is not too useful but I am including it to remind myself it exists. 


m.save('./renewableEnergyPct2023.html')
