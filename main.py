# System
import logging
# Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
# Local project
from dashengine.dashapp import dashapp
import dashengine.navigation as navigation


# Setup logging level
logging.basicConfig(level=logging.DEBUG)

# Setup 'app' variable for GAE
app = dashapp.server

# Read page modules
ALL_PAGES = navigation.page_loader(["pages", "stdpages"])
NAV_BAR = navigation.navigation_bar(ALL_PAGES)

dashapp.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@dashapp.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
def display_page(pathname: str) -> html.Div:
    if pathname in ALL_PAGES:
        return [NAV_BAR, ALL_PAGES[pathname].layout()]
    else:
        return '404'


if __name__ == '__main__':
    dashapp.run_server(debug=True)
