import dash
import dash_core_components as dcc
import dash_html_components as html

dash_app = dash.Dash()
app = dash_app.server

dash_app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        This is Dash running on Google App Engine.
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])

if __name__ == '__main__':
    dash_app.run_server(debug=True)
