# Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
# Local project
from dataset import DataSet
import pages.landing   as landing
import pages.profiling as profiling
import dashapp

dash_app = dashapp.app
app = dash_app.server

# Setup dataset cache
ds = DataSet()
# Prefetch data for this dashboard
ds.prefetch(["met-objects", "met-images"])

dash_app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@dash_app.callback(Output('page-content', 'children'),
                   [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return landing.layout(ds)
    if pathname == '/profile':
        return profiling.layout(ds)
    else:
        return '404'


if __name__ == '__main__':
    dash_app.run_server(debug=True)
