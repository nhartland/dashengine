# System
import logging
# Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
# Local project
from dashengine.dashapp import dashapp
import dashengine.bigquery as bigquery
import dashengine.pageloader as pageloader


# Setup logging level
logging.basicConfig(level=logging.DEBUG)

# Setup 'app' variable for GAE
app = dashapp.server

# Read page modules
ALL_PAGES = pageloader.page_loader(["pages", "stdpages"])

dashapp.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@dashapp.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
def display_page(pathname: str) -> html.Div:
    menu_opts = [dbc.DropdownMenuItem(mod.LINKNAME, href=mod.ROUTE) for mod in ALL_PAGES.values()]
    if pathname in ALL_PAGES:
        return [ dbc.NavbarSimple(  # First build the navigation bar
                 children=[
                     dbc.NavbarBrand(f"{bigquery.PROJECT_ID}"),
                     dbc.DropdownMenu(
                         nav=True,
                         in_navbar=True,
                         label="Navigation",
                         children=menu_opts
                     ),
                 ],
                 brand=f"{ALL_PAGES[pathname].LINKNAME}",
                 brand_href="/",
                 sticky="top",
                 ),                 # Secondly render the page layout
                 ALL_PAGES[pathname].layout()]
    else:
        return '404'


def navigation_bar(pathname) -> dbc.NavbarSimple:
    """ Builds the navigation bar for the dashboards. """


if __name__ == '__main__':
    dashapp.run_server(debug=True)
