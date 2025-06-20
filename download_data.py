from urllib.request import urlretrieve
import sys

url = sys.argv[1]
filename = sys.argv[2]

try:
    urlretrieve(url,filename)
    print(f"File saved.")
except Exception as e:
    print(f"Error downloading file: {e}")



# download_file('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json', "/workspaces/greener/static/usa.geojson")
# download_file("https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv?t=1749639773", "/workspaces/greener/static/home_values.csv")
#download_file("https://files.zillowstatic.com/research/public_csvs/zhvi/County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv?t=1750261630", "/workspaces/greener/static/home_values_county.csv")