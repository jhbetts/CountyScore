import geopandas as gpd
import pandas as pd
geodf = gpd.read_file("/workspaces/greener/shapefile/cb_2018_us_zcta510_500k.shp")
# geodf.to_file(filename="/workspaces/greener/static/usa.geojson", driver="geoJSON")
housing = pd.read_csv("https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv?t=1749639773")
geodf.explore()