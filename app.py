from dash import Dash, html, dcc, Output, Input, callback, dash_table
from plot_usa_map import plot_usa_map, get_map
import dash_bootstrap_components as dbc
import pandas as pd
from urllib.parse import urlencode
app = Dash(external_stylesheets=[dbc.themes.FLATLY])

counties = get_map()
county_data = pd.read_parquet("static/greener/compiled_data.parquet")
test = 'test'



app.layout = html.Div([
    dcc.Store(id='selected-county'),
    dcc.Store(id='county-data'),
    html.H1(children="Greener"),
    html.Div(
        [
            dbc.Row([
                dbc.Col(dcc.Graph(figure=plot_usa_map(counties, county_data), id='map'),width=8),
                # dbc.Col(dash_table.DataTable(id='click-data'), width=4)
                dbc.Col(dbc.Card([html.Div('State:', id='state-name'),
                                html.Div('County:', id='county-name'),
                                html.Div('Average Home Values:', id='home-values'),
                                html.Div(children=[html.A(children='zillow',id='zillow-url')])],
                                    id='county-card'), width=4)
            ])
        ]
    ),
    # html.Div(id='click-data')
])

@callback(
        Output("state-name", 'children'),
        Input('county-data', 'data')
)
def update_state(data):
    if data:
        return f"State: {data[0]["StateName"]}"
    else: return

@callback(
        Output("county-name", 'children'),
        Input('county-data', 'data')
)
def update_state(data):
    if data:
        return f"County: {data[0]["RegionName"]}"
    else:
        return
@callback(
        Output("home-values", 'children'),
        Input('county-data', 'data')
)
def update_state(data):
    if data:
        return f"Average Home Values: {data[0]["AverageHomeValue"]}"
    else:
        return
@callback(
        Output("zillow-url", 'href'),
        Input('county-data', 'data')
)
def update_state(data):
    if data:
        return data[0]["Houses"]
    else: return
@callback(
        Output("county-data", 'data'),
        Input("selected-county", 'data')
)
def update_table(county):

    houses_url_base = 'https://www.zillow.com/'
    if county:
        data = county_data[county_data.fips == county]
        data = data[['StateName', 'RegionName', 'AverageHomeValue']]
        county_formatted = data.iloc[0]["RegionName"].replace(" ", "-")
        data['Houses'] = f'{houses_url_base}{county_formatted}-{data.iloc[0]['StateName']}'
        return data.to_dict('records')
    else: return
@callback(
    Output('selected-county', 'data'),
    Input('map', 'clickData')
)
def display_click_data(clickData):
    data = clickData
    if data:
        res = data['points'][0]['customdata']
        county = res[0]
        value = res[1]
        code = res[2]
        return code
    else:
        return
if __name__ == '__main__':
    app.run(debug=True)