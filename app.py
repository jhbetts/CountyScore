from dash import Dash, html, dcc, Output, Input, callback, dash_table
from plot_graphs import plot_usa_map, get_map, plot_top_ten
import dash_bootstrap_components as dbc
import pandas as pd
from urllib.parse import urlencode
app = Dash(external_stylesheets=[dbc.themes.FLATLY])

counties = get_map()
county_data = pd.read_parquet("static/greener/compiled_data.parquet")
test = 'test'

# dropdown = html.Div(dbc.DropdownMenu(
#     [
#         # dbc.DropdownMenuItem("Home Values"),
#         # dbc.DropdownMenuItem("Median Household Income"),
#         # dbc.DropdownMenuItem("Avg. Summer Temp."),
#         # dbc.DropdownMenuItem("Avg. Winter Temp."),
#         dbc.RadioItems(options=[
#             {'label': "None", 'value': 0},
#             {'label': "Housing", 'value': 1},
#             {'label': "Median Household Income", 'value': 2},
#             {'label': "Avg. Summer Temp.", 'value': 3},
#             {'label': "Avg. Winter Temp.", 'value': 4},
#         ])
#     ],
#     label='Criteria',
#     menu_variant='dark',
#     id='criteria-drop'
# ))

dropdown = html.Div([
    dcc.Dropdown(
        options = {
            'HousingScore':'Home Values',
            'IncomeScore': 'Median Household Income',
            "UnemploymentScore": "Unemployment Rate",
            # "SummerAvg": 'Avg. Summer Temp.',
            # "WinterAvg": 'Avg. Winter Temp.'
            },
        value = 'HousingScore',
        id='criteria-drop',
        multi=True,
        placeholder="Select Your Criteria")
])

list_group = dbc.ListGroup(
    [
        dbc.ListGroupItem([html.Span(children="County"), html.Span(id='county-name', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="State"), html.Span(id='state-name', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Average Home Value"), html.Span(id='home-values', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Zillow"), html.A(id='zillow-url', style={'float': 'right'}, target='_blank')]),
        dbc.ListGroupItem([html.Span(children="Median Household Income"), html.Span(id='hhi', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Unemployment"), html.Span(id='unemployment', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Average Summer Temperature"), html.Span(id='summer-temp', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Average Winter Temperature"), html.Span(id='winter-temp', style={'float': 'right'})]),
        # dbc.ListGroupItem([html.Span(children="Indeed"), html.Span(id='indeed-url', style={'float': 'right'})]),
    ],
)



app.layout = html.Div([
    dcc.Store(id='selected-county'),
    dcc.Store(id='county-data'),
    html.H1(children="Greener", id = 'title'),
    html.Div(
        [
            dbc.Row([
                dbc.Col([dropdown,dcc.Graph(figure=plot_usa_map(counties, county_data, [["HousingScore"]]), id='map')],width={'size':8}),
                dbc.Col(list_group, width=4)
            ]),
            dbc.Row([
                dcc.Graph(figure = plot_top_ten(county_data, [['HousingScore']]), id='top-ten')
            ])
        ]
    ),
    # html.Div(id='click-data')
],)

# Dropdown
@callback(
        Output("map",'figure'),
        Output("top-ten", 'figure'),
        Input("criteria-drop", 'value')
)
def update_criteria(value):
    value = value
    return (plot_usa_map(counties, county_data, [value]), plot_top_ten(county_data, [value]))

# Clicking county on map updates 'selected-county' Store item with the fips code of the county selected.
@callback(
    # Output('selected-county', 'data'),
    Output("county-name", 'children'),
    Output("state-name", 'children'),
    Output("home-values", 'children'),
    Output("zillow-url", 'children'),
    Output("zillow-url", 'href'),
    Output("unemployment", 'children'),
    Output("hhi", 'children'),
    Output("winter-temp", 'children'),
    Output("summer-temp", 'children'),
    Input('map', 'clickData')
)
def display_click_data(clickData):
    data = clickData
    if data:
        res = data['points'][0]['customdata']
        county = res[0]
        state = res[1]
        avg_home = f"${res[2]:,.2f}"
        zillow = res[3]
        unemploy = f"{res[4]:.2f}%"
        hhi = f"${res[5]:,.2f}"
        avg_summer = f"{res[6]}°F"
        avg_winter = f"{res[7]}°F"
        code = res[8]
        results = (county, state, avg_home, zillow, zillow, unemploy, hhi, avg_summer, avg_winter)
        return results
    else:
        return ('','','','','','','','','')


if __name__ == '__main__':
    app.run(debug=True)