# System
import logging
# Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
# Local project
from dashengine.dashapp import dashapp
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


def navigation_bar(pathname) -> dbc.NavbarSimple:
    """ Builds the navigation bar for the dashboards. """
    menu_opts = [dbc.DropdownMenuItem(mod.LINKNAME,
                                      href=mod.ROUTE,
                                      active=(pathname == mod.ROUTE))
                 for mod in ALL_PAGES.values()]
    return dbc.NavbarSimple(children=[
                            # Uncomment to display the project ID in the NavBar
                            #  dbc.NavbarBrand(f"{bigquery.PROJECT_ID}"),
                            dbc.DropdownMenu(
                                nav=True,
                                in_navbar=True,
                                label="Navigation",
                                children=menu_opts)],
                            brand=f"{ALL_PAGES[pathname].TITLE}",
                            brand_href="/",
                            sticky="top",
                            )


@dashapp.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
def display_page(pathname: str) -> html.Div:
    if pathname in ALL_PAGES:
        return [ navigation_bar(pathname),
                 ALL_PAGES[pathname].layout()]
    else:
        return '404'


if __name__ == '__main__':
    dashapp.run_server(debug=True)
