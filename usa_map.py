import geopandas as gp
import plotly

usa = gp.read_file('/workspaces/greener/shapefile/cb_2018_us_zcta510_500k.shp')
# Plot a interactive map of the data
usa.plot()