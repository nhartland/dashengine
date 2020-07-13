# Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Local project
from dashengine.dashapp import dashapp, cache
from dashengine.dashapp import CONFIGURATION
import dashengine.pageloader as pageloader

# Setup 'app' variable for GAE
app = dashapp.server

# Read page modules
ALL_PAGES = pageloader.page_loader(["pages", "stdpages"])

# Application Name
APP_NAME = CONFIGURATION["APP_NAME"]


dashapp.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),  # URL Storage
        dcc.Store(id="refresh-status", data=0),  # Refresh status storage
        dbc.NavbarSimple(
            children=[
                dbc.DropdownMenu(
                    id="global-navigation", nav=True, in_navbar=True, label="Navigation"
                ),
                dbc.NavLink("Refresh", id="refresh-button", n_clicks=0, href="#"),
            ],
            sticky="top",
            brand=APP_NAME,
            brand_href="/",
        ),
        html.Div(className="container", id="page-content"),
    ]
)


@dashapp.callback(Output("global-navigation", "children"), [Input("url", "pathname")])
def navigation_dropdown(pathname) -> list:
    """ Builds the navigation dropdown for the dashboards. """
    return [
        dbc.DropdownMenuItem(
            mod.LINKNAME, href=mod.ROUTE, active=(pathname == mod.ROUTE)
        )
        for mod in ALL_PAGES.values()
    ]


@dashapp.callback(
    Output("refresh-status", "data"), [Input("refresh-button", "n_clicks")]
)
def refresh_cache(num_clicks):
    with app.app_context():
        cache.clear()
    return num_clicks


# Updates either on change of URL or change of refresh-status
@dashapp.callback(
    Output("page-content", "children"),
    [Input("url", "pathname"), Input("refresh-status", "data")],
)
def display_page(pathname: str, _) -> list:
    if pathname in ALL_PAGES:
        return ALL_PAGES[pathname].layout()
    else:
        return "404"


if __name__ == "__main__":
    dashapp.run_server(host="0.0.0.0", debug=True)
