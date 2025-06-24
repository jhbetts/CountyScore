from urllib.request import urlretrieve
# import sys

# url = sys.argv[1]
# filename = sys.argv[2]

# try:
#     urlretrieve(url,filename)
#     print(f"File saved.")
# except Exception as e:
#     print(f"Error downloading file: {e}")

def download_data(url,filename):
    try:
        urlretrieve(url,filename)
        print(f"File saved.")
    except Exception as e:
        print(f"Error downloading file: {e}")

download_data('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json',
            "static/greener/usa.geojson")

# county geojson: 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json' "C:\Users\Hunter\Documents\greener\static\greenerusa.geojson"
# Zillow zip: "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv?t=1749639773" "static\greener/home_values_zip.csv"
# Zillow county: "https://files.zillowstatic.com/research/public_csvs/zhvi/County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv?t=1750261630" "static/greener/home_values_county.csv"