import pandas as pd

# This script downloads median home values from Zillow. It contains data for over 26,000 zip codes.
# This script may be changed to use API calls instead. API can be found at https://bridgedataoutput.com/overview

data = pd.read_csv("https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv?t=1749639773")

data_recency = data.columns
