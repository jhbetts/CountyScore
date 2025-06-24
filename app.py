from dash import Dash, html, dcc, Output, Input, callback, dash_table
from plot_usa_map import plot_usa_map
import json

app = Dash()

app.layout = [
    html.H1(children="Greener"),
    dcc.Graph(figure=plot_usa_map(), id='map'),
    html.Div(id='click-data')
]

@callback(
    Output('click-data', 'children'),
    Input('map', 'clickData')
)
def display_click_data(clickData):
    data = clickData
    if data:
        res = data['points'][0]['customdata']
        county = res[0]
        value = res[1]
        code = res[2]
        return res
    else:
        return
if __name__ == '__main__':
    app.run(debug=True)