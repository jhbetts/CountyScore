import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from helpers import download_data
import requests
us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "Virgin Islands, U.S.": "VI",
}

def open_csv_data(filename, url):
    try:    
        x = pd.read_csv(filename, comment='#')
    except:
        download_data(url, filename)
        x = pd.read_csv(filename, comment="#")
    return x

def get_pop():
    df = pd.read_excel("https://www2.census.gov/programs-surveys/popest/tables/2020-2024/counties/totals/co-est2024-pop.xlsx", usecols='A,G',skiprows=4, names=['Region','Pop_Est_July_1_2024'])
    df['Region'] = df['Region'].apply(lambda x: str(x).replace('.',''))
    df[["County", "State"]] = df["Region"].str.split(",", expand=True, n=1)
    df.drop("Region", axis=1,inplace=True)
    df['State'] = df['State'].str.strip()
    df['State'] = df['State'].replace(us_state_to_abbrev)
    df.dropna(inplace=True)
    df['Pop_Est_July_1_2024'] = df['Pop_Est_July_1_2024'].astype(int)
    scaler = MinMaxScaler()
    df['Low_Pop_Score'] = 1 - scaler.fit_transform(np.log10(df[["Pop_Est_July_1_2024"]]))
    df['High_Pop_Score'] = scaler.fit_transform(np.log10(df[["Pop_Est_July_1_2024"]]))
    return df


def get_homes():
    housing = open_csv_data("static/county_score/home_values_county.csv","https://files.zillowstatic.com/research/public_csvs/zhvi/County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv?t=1750261630")
    
    # Ensure StateCodeFIPS is in two digit format and MunicipalCodeFIPS is in 3 digit format.
    housing["StateCodeFIPS"] = housing["StateCodeFIPS"].apply(lambda x: str(x).zfill(2))
    housing["MunicipalCodeFIPS"] = housing['MunicipalCodeFIPS'].apply(lambda x: str(x).zfill(3))

    # Combine State and Municipal FIPS codes to get a 5 digit FIPS code.
    housing.insert(0,"Fips",(housing["StateCodeFIPS"] + housing["MunicipalCodeFIPS"])) 
    housing["Fips"]= housing["StateCodeFIPS"] + housing["MunicipalCodeFIPS"]
    # Rename most recent column to "AverageHomeValue" so code is usable with updated csv files.
    housing = housing.rename(columns={housing.columns[-1]:"AverageHomeValue"})

    # Convert "AverageHomeValue" to float32 to decrease memory usage.
    housing['AverageHomeValue'] = housing['AverageHomeValue'].astype(np.float32)

    # Select only used columns
    housing = housing[['Fips', 'StateName', "RegionName", 'AverageHomeValue']]

    # Normalize the values in a new column.
    scaler = MinMaxScaler()
    housing['HousingScore'] = 1 - scaler.fit_transform(np.log10(housing[["AverageHomeValue"]]))
    # Create zillow url
    houses_url_base = 'https://www.zillow.com/'
    housing['Houses'] = housing.apply(lambda row: f'{houses_url_base}{row["RegionName"].replace(" ", "-")}-{row['StateName']}', axis=1)
    return housing

def get_temps(filename, url):
    temps = open_csv_data(filename,url)
    temps = temps[['Name', 'Value', 'State']]
    temps['State'] = temps['State'].replace(us_state_to_abbrev)
    temps = temps[['Name', 'Value', 'State']]
    scaler = MinMaxScaler()
    temps['Low_Temp_Score'] = 1 - scaler.fit_transform(np.log10(temps[["Value"]]))
    temps['High_Temp_Score'] = scaler.fit_transform(np.log10(temps[["Value"]]))

    return temps

def get_unemployment(filename, url):
    df = open_csv_data(filename, url)
    df['FIPS_Code'] = df['FIPS_Code'].apply(lambda x: str(x).zfill(5))
    df = df[df['Attribute'].isin(['Unemployment_rate_2023', 'Median_Household_Income_2022'])]
    df = df.pivot(index='FIPS_Code', columns='Attribute', values='Value')
    scaler = MinMaxScaler()
    df['IncomeScore'] = scaler.fit_transform(np.log10(df[['Median_Household_Income_2022']]))
    df['UnemploymentScore'] = 1 - scaler.fit_transform(np.log10(df[['Unemployment_rate_2023']]))
    df.index.names=['Fips']
    return df

def get_politics(states):
    for state in states:
        name = next(key for key, value in us_state_to_abbrev.items() if value == state)
        name = name.replace(' ', '-')
        states[states==state] = name.lower()
    states = np.delete(states, np.where(states=='district-of-columbia'))
    counties = pd.DataFrame(columns=['Fips','Name', "R_Votes", "D_Votes", "Total_Votes"])
# define function to scrape page
    def get_results(state: str):
        url = f"https://static01.nyt.com/elections-assets/pages/data/2024-11-05/results-{state}-president.json"
        response = requests.get(url)
        data = response.json()
        race = data.get('races')
        race = race[0]
        units = race.get("reporting_units")
        for unit in units:
            name = unit.get('name')
            level= unit.get('level')
            if level in ['county', 'township']:
                Fips = unit.get('fips_state')+unit.get('fips_county')
                candidates=unit.get("candidates")
                for candidate in candidates:
                    id = candidate['nyt_id']
                    if id == 'harris-k':
                        d_votes = candidate['votes']['total']
                    elif id == 'trump-d': 
                        r_votes = candidate['votes']['total']
                    else: pass
                total = unit.get('total_votes')
                counties.loc[len(counties)] = [Fips, name, r_votes, d_votes, total]
            else: pass
    # call function on all selected states
    for state in states:
        get_results(state)
    # get DC results
    get_results('washington-dc')
    # Some states have multiple reporting units per county. Compile those into county results using the Fips.
    counties = counties.groupby(counties['Fips'], as_index=False).aggregate({'Fips': 'first', 'R_Votes':"sum", 'D_Votes': 'sum', 'Total_Votes': 'sum'})
    # Score for liberal vs conservative by dividing each parties votes by total votes.
    counties['R_Score'] = counties['R_Votes']/counties['Total_Votes']
    counties['D_Score'] = counties['D_Votes']/counties['Total_Votes']
    return counties


def compile_data():
    housing = get_homes()
    winter = get_temps("static/county_score/dec_feb_temps.csv",
                        "https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/county/mapping/110-tavg-202412-3.csv")
    winter.rename(columns={"Value":"WinterAvg", "High_Temp_Score": "Winter_High_Temp_Score", "Low_Temp_Score": "Winter_Low_Temp_Score"}, inplace=True)
    summer = get_temps("static/county_score/jun_aug_temps.csv",
                    "https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/county/mapping/110-tavg-202408-3.csv")
    summer.rename(columns={"Value": "SummerAvg", "High_Temp_Score": "Summer_High_Temp_Score", "Low_Temp_Score": "Summer_Low_Temp_Score"}, inplace=True)
    winter = winter.merge(summer)
    joined = pd.merge(housing, winter, right_on=["Name", 'State'], left_on=['RegionName', 'StateName'], how='left')
    joined.drop(columns=['Name', 'State'], inplace=True)
    # codes = joined['Fips'].unique()
    unemploy = get_unemployment('static/county_score/unemployment_hhi_2000-23.csv',"https://ers.usda.gov/sites/default/files/_laserfiche/DataFiles/48747/Unemployment2023.csv?v=67344")
    # Possibly replace with merge
    # unemploy = unemploy[unemploy.index.isin(codes)]
    joined = joined.merge(unemploy, on='Fips', how='left')
    jobs_url_base = 'https://www.indeed.com/jobs?q=&l='
    joined['Jobs'] = housing.apply(lambda row: f'{jobs_url_base}{row["RegionName"].replace(" ", "+")}%2C+{row['StateName']}', axis=1)
    joined['Summary']=None
    pop = get_pop()
    joined = joined.merge(pop, left_on=['RegionName', "StateName"], right_on=['County', 'State'], how='left')
    joined.drop(columns=['County', 'State'], inplace=True)
    states = joined['StateName'].unique()
    politics = get_politics(states)
    joined = joined.merge(politics, on='Fips', how='left')
    joined['Selected'] = None
    joined.to_parquet('static/county_score/compiled_data.parquet')

compile_data()