import plotly.express as px
import pandas as pd
from google import genai
from google.genai import types
import os
import json


def download_data(url,filename):
    from urllib.request import urlretrieve

    try:
        urlretrieve(url,filename)
        print(f"File saved.")
    except Exception as e:
        print(f"Error downloading file: {e}")

def get_map():
    try:
        with open("static/county_score/usa.geojson") as f:
            counties = json.load(f)
    except:
        download_data('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json',
                    "static/county_score/usa.geojson")
        with open("static/county_score/usa.geojson") as f:
            counties = json.load(f)
    return counties

def plot_top_ten(data,columns):
    if columns[0]:
        score = pd.DataFrame()
        score['Score'] = data[columns[0]].sum(axis=1, skipna=True)
    else: 
        score = pd.DataFrame()
        score['Score'] = [0]* data.shape[0]
    score = score.merge(data[['Fips','RegionName', 'StateName']], left_index=True, right_index=True, how='inner')
    top_ten = score.sort_values('Score', ascending=False).head(10)
    fig = px.bar(top_ten, x = 'Fips', y = 'Score', labels={"Fips": "Top Ten Counties"},
                custom_data=['Fips', 'RegionName', "StateName", 'Score'],

                )
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(xaxis={'categoryorder': 'total descending'}, 
                      plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)',
                      font = {'color': '#234d2c', 'size': 20},)
    fig.update_traces(marker_color = 'rgba(35,139,69,1.0)',
                      hovertemplate="<b>%{customdata[1]}, %{customdata[2]}</b><br>"+
                                    "<b>Score: %{customdata[3]:.2f}</b><br>")
    return fig


def plot_usa_map(map, data, columns, selected=None):
    import plotly.graph_objects as go
    dummy_columns = ['HousingScore', 'IncomeScore']
    if columns[0]:
        score = pd.DataFrame()
        score['Total'] = data[columns[0]].sum(axis=1, skipna=True)
    else: 
        score = pd.DataFrame()
        score['Total'] = [0]* data.shape[0]
    if selected:
        data['Selected'] = None
        data.loc[data['Fips'] == selected, 'Selected'] = 1
    fig = px.choropleth_map(data, geojson=map, locations="Fips", color=score['Total'],
                            color_continuous_scale='greens',
                            map_style='carto-positron-nolabels',
                            zoom=3, center={'lat': 37.0902, 'lon': -95.7129},
                            opacity=1.0,
                            custom_data=["RegionName", 
                                         "StateName", 
                                         "AverageHomeValue", 
                                         "Houses", 
                                         'Unemployment_rate_2023', 
                                         'Median_Household_Income_2022', 
                                         "WinterAvg", 
                                         "SummerAvg", 
                                         "Fips", 
                                         score['Total']])
    fig.update_traces(hovertemplate="<b>%{customdata[0]}, %{customdata[1]}</b><br>"+
                                    "<b>Score: %{customdata[9]:.2f}</b><br>")
    fig.add_trace(go.Choroplethmap(geojson=map, locations=data["Fips"], z= data['Selected'],
                        colorscale = [[0, 'green'],[.5,'red'],[1, 'green']],
                        marker_opacity=1.,
                        showscale=False
                            )
                        )
    fig.update_layout(margin={"r":0,"l":0,"t":0,"b":0})
    fig.update_coloraxes(showscale=False)
    return fig


def ai_copy(county,state):
    key = os.getenv("MY_API_KEY")
    client = genai.Client(api_key=key)

    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=f'''In 150-200 words, give me an summary of {county} {state}. Touch on things like the largest employers,
        fun things to do, and scenery. Include the nearest city of more than 50,000. 
        Give a neutral response that does not sound like an advertisement for the county.''',
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
    )
    return response.text