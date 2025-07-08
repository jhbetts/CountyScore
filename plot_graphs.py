import plotly.express as px
import pandas as pd

def get_map():
    from download_data import download_data
    import json

    try:
        with open("static/greener/usa.geojson") as f:
            counties = json.load(f)
    except:
        download_data('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json',
                    "static/greener/usa.geojson")
        with open("static/greener/usa.geojson") as f:
            counties = json.load(f)
    return counties

def plot_top_ten(data,columns):
    if columns[0]:
        score = pd.DataFrame()
        score['Score'] = data[columns[0]].sum(axis=1, skipna=True)
    else: 
        score = pd.DataFrame()
        score['Score'] = [0]* data.shape[0]
    score = score.merge(data[['fips','RegionName', 'StateName']], left_index=True, right_index=True, how='inner')
    top_ten = score.sort_values('Score', ascending=False).head(10)
    fig = px.bar(top_ten, x = 'RegionName', y = 'Score', labels={"RegionName": "Top Ten Counties"},
                custom_data=['fips']
                )
    fig.update_layout(xaxis={'categoryorder': 'total descending'}, 
                      plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)',
                      font = {'color': 'white'}, 
                    )
    fig.update_traces(marker_color = 'rgba(35,139,69,1.0)')
    return fig


def plot_usa_map(map, data, columns):

    dummy_columns = ['HousingScore', 'IncomeScore']
    if columns[0]:
        score = pd.DataFrame()
        score['Total'] = data[columns[0]].sum(axis=1, skipna=True)
    else: 
        score = pd.DataFrame()
        score['Total'] = [0]* data.shape[0]

    fig = px.choropleth_map(data, geojson=map, locations="fips", color=score['Total'],
                            color_continuous_scale='greens',
                            map_style='carto-darkmatter-nolabels',
                            zoom=3, center={'lat': 37.0902, 'lon': -95.7129},
                            opacity=1.0,
                            title="Average Home Value By County", 
                            hover_name="RegionName",
                            hover_data={'fips': False, "HousingScore": False},
                            custom_data=["RegionName", "StateName", "AverageHomeValue", "Houses", 'Unemployment_rate_2023', 'Median_Household_Income_2022', "WinterAvg", "SummerAvg", "fips"])
    
    fig.update_layout(margin={"r":0,"l":0,"t":0,"b":0})
    fig.update_coloraxes(showscale=False)
    return fig
