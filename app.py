from dash import Dash, html, dcc, Output, Input, callback, ctx
from helpers import plot_usa_map, get_map, plot_top_ten, ai_copy
import dash_bootstrap_components as dbc
import pandas as pd
# from urllib.parse import urlencode

app = Dash(external_stylesheets=[dbc.themes.FLATLY, 'static/greener/style.css'])

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
            {'label': "More Liberal", 'value': 'D_Score', 'disabled':False},
            {'label': "More Conservative", 'value': 'R_Score', 'disabled':False},
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
        dbc.ListGroupItem([html.Span(children="County", className='list-label'), html.Span(id='county-name', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="State",className='list-label'), html.Span(id='state-name', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Population",className='list-label'), html.Span(id='population', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Average Home Value",className='list-label'), html.Span(id='home-values', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Zillow",className='list-label'), html.A(id='zillow-url', style={'float': 'right'}, target='_blank')]),
        dbc.ListGroupItem([html.Span(children="Median Household Income",className='list-label'), html.Span(id='hhi', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Unemployment",className='list-label'), html.Span(id='unemployment', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Average Summer Temperature",className='list-label'), html.Span(id='summer-temp', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Average Winter Temperature",className='list-label'), html.Span(id='winter-temp', style={'float': 'right'})]),
        dbc.ListGroupItem([html.Span(children="Indeed",className='list-label'), html.A(id='jobs-url', style={'float': 'right'}, target='_blank')]),
        dbc.ListGroupItem([html.Span(children="Summary",className='list-label'), html.Br(),html.Span(id='ai-summary', style={'float': 'right',})],style={'minHeight': '40vh',}),
    ],
    flush=True,
)

info_card = dbc.Card(
    [        
        dbc.CardHeader(html.H3(children='County Summary', className='text-success')),
        list_group,
        dbc.CardFooter(html.P("Summary by Google Gemini", className="text-success"))   
    ],
    style={'height': '100vh'}
)

# tab1_content =dbc.Card(
#         dbc.Container(
#                 html.Div(
#                     [
#                         dbc.Row(
#                             [dbc.Col(
#                                 [
#                                     dropdown,
#                                     html.Div(
#                                     dcc.Graph(figure=plot_usa_map(counties, county_data, [["HousingScore"]]), id='map', responsive=True,style={'minHeight': '55vh',}),
#                                     ),
#                                     html.Div(
#                                         dcc.Graph(figure = plot_top_ten(county_data, [['HousingScore']]), id='top-ten',style={'minHeight': '40vh'}),
#                                     )
#                                 ]
#                                 ),
#                             dbc.Col(
#                                 [
#                                     info_card
#                                 ]
#                             )
#                             ]
#                         )
#                     ]
#                 ),
#                 style={'padding': '25px'},
#                 fluid=True
#             )
#         )
tab1_content =dbc.Card(
        dbc.Container(
                html.Div(
                    [
                        dbc.Row(
                            [dbc.Col(
                                [
                                    dropdown,
                                    html.Div(
                                        dcc.Loading(
                                            dcc.Graph(figure=plot_usa_map(counties, county_data, [["HousingScore"]]), id='map', responsive=True,style={'minHeight': '55vh',}),
                                            overlay_style={"visibility":"visible", "filter": "blur(2px)"},
                                            type="circle",
                                            custom_spinner=dbc.Spinner(color="#b7cbb2")
                                        )
                                    ),
                                    html.Div(
                                        dcc.Graph(figure = plot_top_ten(county_data, [['HousingScore']]), id='top-ten',style={'minHeight': '40vh'}),
                                    )
                                ]
                                ),
                            dbc.Col(
                                [
                                    dcc.Loading(
                                        info_card,
                                        overlay_style={"visibility":"visible", "filter": "blur(2px)"},
                                        type="circle",
                                        custom_spinner=dbc.Spinner(color="#266333")
                                    )
                                ]
                            )
                            ]
                        )
                    ]
                ),
                style={'padding': '25px'},
                fluid=True
            )
        )


tab2_content = dbc.Card(
    html.Div(
        [        
            dcc.Markdown('''
                    ## About

                    *Same Grass, But Greener* is a data visualization tool that lets users see the relationship between different factors based on county level data in an effort to provide users with actionable information when looking to make a move. Users can select the criteria they wish to view, and either pan around the map, selecting counties based on their shading, or select from the top ten counties shown in the bar graph beneath the map.

                    ### How are counties scored?

                    Counties are scored with log10 and min-max scaling and as ratios. Applying the scaling results in a score from 0 to 1 for each variable of each county. Scores are summed based on the criteria selected by the user, and those sums are used to rank and map the counties.

                    #### Log10 Scaling

                    Log-10 scaling is the practice of converting each datapoint to is log10 value. Doing this addresses the skewnewss of the data. For example, prior to applying log10 scaling to the home value data, a handfull of counties with average home values in the millions created a skewed dataset, where home prices from $100,000 to $500,000 were effectively the same spot on the scale. Using log10 scaling means that while high values are still represented at the top of the scale, there is greater variation between lower values, where most of the data resides.

                    Data that was scaled with log10 scaling: Average Home Values

                    #### Min-Max Scaling

                    Min max scaling is the practice of scaling numerical values down to fit within a specified range, in this case 0-1. The lowest number in the dataset will be given a value of 0, and the highest a value of 1. The remaining numbers are placed on the spectrum between 0 and 1. This process makes it easier to compare values of different scales. For example, the average home value of a county could realistically be $1,000,000, but it is unlikely that a counties median annual income would be that high. Instead, $100,000 is a more realistic number. Because of this variation, if we compared a county with $1,000,000 homes and $200,000 incomes to one with with $500,000 homes and $100,000 incomes, the county with the higher incomes would likely score worse due to the large nominal difference in home prices, when clearly they are proportial to the income prices. The very high home value is skewing the results. In order to compare incomes and home values across counties, we need to scale the values so that a county with very high median income (e.g. $100,000) and a county with a very average high home value (e.g. $1,000,000) both carry the same weight.

                    Data that was scored via min-max scaling: Average Home Values, Median Household Income, Average Temperatures, Unemployment Rate, Population

                    #### Ratios

                    Ratios are the direct relationships between two numbers. For example, a county with 50,000 Democratic votes and 100,000 Republican votes has a Democratic to Republican ratio of 1:2, or .5. Ratio scoring was chosen for data that contains two diametrically opposed variables. This is a simple way to score the variables when the relationship between those two variables is more important than the variables themselves.

                    Data that was scored via ratio: Political Affiliation

                    ### About the Data

                    #### Average Home Values
                    Source: [Zillow Average Home Value](https://files.zillowstatic.com/research/public_csvs/zhvi/County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv?t=1750261630)

                    Zillow publishes monthly reports on the average home sales prices in each county in the United States. From this data I extract the most recent month's average price, scale those prices with log10, and then score them from 0-1, with 0 being the highest prices and 1 being the lowest. This inverse min-max scaling is used with the assumption that lower home prices are better when deciding where to live. 

                    #### Average Winter and Summer Temperatures
                    Source: [NOAA Average Temperature Between December 2024 and February 2025](https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/county/mapping/110-tavg-202502-3.csv), [NOAA Average Temperature Between June and August 2024](https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/county/mapping/110-tavg-202408-3.csv)

                    The National Centers for Environmental Information provides county level data as part of their "Climate at a Glance" platform. This data is downloaded in .csv format, and scored using min-max scaling to create four score values for each state: "Summer_High_Temp_Score", "Summer_Low_Temp_Score", "Winter_High_Temp_Score", and "Winter_Low_Temp_Score". This combination allows users to filter for whatever combination of winter and summer temperatures they prefer. 

                    #### Population Estimates
                    Source: [2020-2024 Census Population Data](https://www2.census.gov/programs-surveys/popest/tables/2020-2024/counties/totals/co-est2024-pop.xlsx)

                    Provided by the Census Beureau, this data contains county level population estimates for July of 2020, 2021, 2022, 2023, and 2024. From this data the most recent estimates are selected and scored via min-max scaling to create two scores: "Low_Pop_Score" and "High_Pop_Score". This allows users to choose how the population size of counties should be scored based on their preferences.

                    #### Unemployment Rate and Median Household Income
                    Source: [County Level Unemployment and Household Income Data from the USDA](https://ers.usda.gov/sites/default/files/_laserfiche/DataFiles/48747/Unemployment2023.csv?v=67344)

                    The Economic Research Service of the U.S. Department of Agriculture provides a county level unemployment and household income dataset that supplies the annual average income 2023 unemployment and 2022 median income of US counties. These two variables are then scaled using min-max scaling to create scores for each county. The unemployment score is inversed, meaning that a lower unemployment value creates a higher score.

                    #### County Political Leaning
                    Source: Scraped from [The New York Times](https://www.nytimes.com/)

                    Precinct level vote counts are scraped from the New York Times and compiled into county level totals of votes for the Democratic and Republican nominees in the 2024 Presidential Election. Total are then compared to the total number of votes cast as a ratio, which serve as the "R_Score" and "D_Score" for that county. Counties with a higher "R_Score" are said to be "More Conservative" and counties with a higher "D_Score" are said to be more conservative. 

                    ### Built with...
                    '''
                ),
                html.Div(
                    [
                        html.Img(src="/static/greener/python-logo-only.svg", style={'max-height': '100px','padding': '0px 0px 0px 0px'}),
                        html.Img(src="https://plotly-marketing-website-2.cdn.prismic.io/plotly-marketing-website-2/Z7eNlJ7c43Q3gCJv_Plotly-Logo-Black.svg",style={'max-height': '150px', 'padding-bottom': "10px"}),
                        html.Img(src="https://pandas.pydata.org/static/img/pandas.svg",style={'max-height': '150px'}),
                        html.Img(src="https://upload.wikimedia.org/wikipedia/commons/8/8a/Google_Gemini_logo.svg",style={'max-height': '100px', 'padding': '0px 0px 30px 50px'}),
                    ],
                    style={ "display": "flex", "justify-content": "center", "align-items": "center"}
                )
        ],        
        style={'padding': '25px'}
    )
)

app.layout = html.Div([
    dcc.Store(id='selected-county'),
    dcc.Store(id='county-data'),
    html.Div(
        [
            html.H1(children="Same Grass, But Greener", id = 'title', className='text-success'),
            html.A(
                [
                    html.Img(src="static/greener/GitHub_Invertocat_Dark.svg", style={'max-height': '50px','padding': '0px 0px 0px 0px','min-height': '50px'})
                ],
                href = "https://github.com/jhbetts/greener",
                target='_blank'
                ),
        ],
        style={ "display": "flex", "justify-content": "space-between", "align-items": "center",}
    ),
    
    dbc.Tabs(
        [
            dbc.Tab(tab1_content, label="Main"),
            dbc.Tab(tab2_content, label='About')
        ]
    )
    ], className = 'dbc'
)

# html.Img(src="static/greener/GitHub_Invertocat_Dark.svg", style={'max-height': '50px','padding': '0px 0px 0px 0px',})

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
        Output("ai-summary", 'children'),
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
        population = f"{row['Pop_Est_July_1_2024'].item():,}"
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
    app.run(debug=False)
