from dash import Dash, html, dcc, Output, Input, callback, ctx
from helpers import plot_usa_map, get_map, plot_top_ten, ai_copy
import dash_bootstrap_components as dbc
import pandas as pd
# from urllib.parse import urlencode

app = Dash(external_stylesheets=[dbc.themes.SLATE, 'static/greener/style.css'])

counties = get_map()
county_data = pd.read_parquet("static/greener/compiled_data.parquet")

dropdown = html.Div([
    dcc.Dropdown(
        [
            {'label': "Low Home Prices", 'value': 'HousingScore', 'disabled':False},
            {'label': "High Income", 'value': 'IncomeScore', 'disabled':False},
            {'label': "Low Unemployment", 'value': 'UnemploymentScore', 'disabled':False},
            {'label': "Warm Summers", 'value': 'Summer_High_Temp_Score', 'disabled':False},
            {'label': "Cool Summers", 'value': 'Summer_Low_Temp_Score', 'disabled':False},
            {'label': "Warm Winters", 'value': 'Winter_High_Temp_Score', 'disabled':False},
            {'label': "Cool Winters", 'value': 'Winter_Low_Temp_Score', 'disabled':False},
        ],
        value = 'HousingScore',
        id='criteria-drop',
        # closeOnSelect=False // Only available in Dash 3.1, which breaks the map,
        multi=True,
        placeholder="Select Your Criteria", 
        style={
            'background-color': '#32383e',
            'color': "rgba(98,196,98,1.0)"
        }
        )
    ],
    className="custom-dropdown"
)

list_group = dbc.ListGroup(
    [
        dbc.ListGroupItem([html.Span(children="County"), html.Span(id='county-name', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="State"), html.Span(id='state-name', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Population"), html.Span(id='population', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Average Home Value"), html.Span(id='home-values', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Zillow"), html.A(id='zillow-url', style={'float': 'right'}, target='_blank')]),
        dbc.ListGroupItem([html.Span(children="Median Household Income"), html.Span(id='hhi', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Unemployment"), html.Span(id='unemployment', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Average Summer Temperature"), html.Span(id='summer-temp', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Average Winter Temperature"), html.Span(id='winter-temp', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Indeed"), html.A(id='jobs-url', style={'float': 'right'}, target='_blank')]),
    ],
)

info_card = dbc.Card(
    [
        list_group,
        html.P(id="ai-output")
    ]
)

app.layout = html.Div([
    dcc.Store(id='selected-county'),
    dcc.Store(id='county-data'),
    html.H1(children="Greener", id = 'title', className='text-success'),
    dbc.Container(
        html.Div(
            [
                dbc.Card(
                    dbc.Row([
                        dbc.Col([dropdown,dcc.Graph(figure=plot_usa_map(counties, county_data, [["HousingScore"]]), id='map')],width={'size':7}),
                        dbc.Col(list_group)
                        ],
                        className='g-1'
                    )
                ),
                html.Br(),
                dbc.Row([
                    dbc.Col(dcc.Graph(figure = plot_top_ten(county_data, [['HousingScore']]), id='top-ten'),width=7),
                    dbc.Col([html.H3(children='County Summary via Google Gemini', className='text-success'),html.P(id="ai-output")])
                    ]
                )
            ]
        ),
        fluid=True
    )
    # html.Div(id='click-data')
], className = 'dbc'
)

# Dropdown
@callback(
        Output("map",'figure'),
        Output("top-ten", 'figure'),
        Input("criteria-drop", 'value')
)
def update_criteria(value):
    value = value
    return (plot_usa_map(counties, county_data, [value]), plot_top_ten(county_data, [value]))

# When "map" or 'top-ten' is clicked, 'selected-county' is updated. 
@callback(
        Output("selected-county", 'data'),
        [Input("top-ten", 'clickData'),
        Input('map', 'clickData')]
)
def output_top_ten(top_ten_click, map_click):
    button_clicked = ctx.triggered_id
    if button_clicked == 'top-ten':
        fips = top_ten_click['points'][0]['customdata'][0]
        return fips
    elif button_clicked == 'map':
        fips = map_click['points'][0]['customdata'][8]
        return fips
    else:
        return None

# When "selected-county" is updated, 'county_data' is queried for row matching the fips code in "selected-county" data.
@callback(
        Output("ai-output", 'children'),
        Output("county-name", 'children'),
        Output("state-name", 'children'),
        Output("home-values", 'children'),
        Output("zillow-url", 'children'),
        Output("zillow-url", 'href'),
        Output("unemployment", 'children'),
        Output("hhi", 'children'),
        Output("jobs-url","children"),
        Output("jobs-url", 'href'),
        Output("winter-temp", 'children'),
        Output("summer-temp", 'children'),
        Output("population", 'children'),
        Input('selected-county', 'data')
)
def get_county_properties(data):
    if data:
        row = county_data[county_data['fips']==data]
        county = row['RegionName'].item()
        state = row['StateName'].item()
        avg_home = f"${row['AverageHomeValue'].item():,.2f}"
        zillow = row['Houses'].item()
        unemploy = f"{row['Unemployment_rate_2023'].item():.2f}%"
        hhi = f"${row['Median_Household_Income_2022'].item():,.2f}"
        avg_summer = f"{row['SummerAvg'].item()}°F"
        avg_winter = f"{row['WinterAvg'].item()}°F"
        jobs = row['Jobs'].item()
        population = row['Pop_Est_July_1_2024']
        if row['Summary'].item() != None:
            summary = row['Summary'].item()
        else:
            county_data.loc[county_data['fips']==data, 'Summary'] = ai_copy(county,state)
            summary = county_data.loc[county_data['fips']==data, 'Summary'].item()
            county_data.to_parquet('static/greener/compiled_data.parquet')

        results = (summary,county, state, avg_home, zillow, zillow, unemploy, hhi,jobs,jobs,  avg_winter,avg_summer, population)
        return results
    else:
        return ('','','','','','','','','','','','','')


if __name__ == '__main__':
    app.run(debug=True)