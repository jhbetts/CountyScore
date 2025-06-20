
def plot_usa_map():
    import json
    import numpy as np
    import pandas as pd
    import plotly.express as px
    with open("/workspaces/greener/static/greener/usa.geojson") as f:
        counties = json.load(f)

        
    housing = pd.read_csv("/workspaces/greener/static/greener/home_values_county.csv")
    # Ensure StateCodeFIPS is in two digit format and MunicipalCodeFIPS is in 3 digit format.
    housing["StateCodeFIPS"] = housing["StateCodeFIPS"].apply(lambda x: str(x).zfill(2))
    housing["MunicipalCodeFIPS"] = housing['MunicipalCodeFIPS'].apply(lambda x: str(x).zfill(3))

    # Combine State and Municipal FIPS codes to get a 5 digit FIPS code.
    housing.insert(0,"fips",(housing["StateCodeFIPS"] + housing["MunicipalCodeFIPS"])) 
    housing["fips"]= housing["StateCodeFIPS"] + housing["MunicipalCodeFIPS"]
    # Rename most recent column to "AverageHomeValue" so code is usable with updated csv files.
    housing = housing.rename(columns={housing.columns[-1]:"AverageHomeValue"})

    # Convert "AverageHomeValue" to float32 to decrease memory usage.
    housing['AverageHomeValue'] = housing['AverageHomeValue'].astype(np.float32)

    # Select only used columns
    housing = housing[['fips', 'StateName', "RegionName", 'AverageHomeValue']]

    # Normalize the values in a new column.
    housing["NormalizedValues"]= np.log10(housing['AverageHomeValue']) 
    fig = px.choropleth_map(housing, geojson=counties, locations="fips", color="NormalizedValues",
                            color_continuous_scale='greens',
                            # range_color=(min_value, max_value),
                            map_style='carto-darkmatter-nolabels',
                            zoom=3, center={'lat': 37.0902, 'lon': -95.7129},
                            opacity=1.0,
                            title="Average Home Value By County", 
                            hover_name="RegionName",
                            hover_data={'AverageHomeValue': ':,.2f', 'fips': False, "NormalizedValues": False},
                            custom_data=["RegionName","AverageHomeValue", "fips"])
    fig.update_layout(margin={"r":0,"l":0,"t":0,"b":0})
    fig.update_coloraxes(showscale=False)
    return fig
plot_usa_map()