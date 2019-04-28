# System
import pkgutil
import importlib
import logging
# Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
# Local project
from dashengine.dashapp import dashapp


def page_loader(roots: list) -> dict:
    """ Reads page modules from subdirectories specified in the `roots` list,
    and returns them in a dictionary keyed by module.ROUTE. """
    page_dict = {}
    for root in roots:
        for importer, package_name, _ in pkgutil.iter_modules([root]):
            full_package_name = '%s.%s' % (root, package_name)
            module = importlib.import_module(full_package_name)
            route = module.ROUTE
            logging.info(f'Page module \"{package_name}\" loaded at route \"{route}\"')
            page_dict[route] = module
    return page_dict


# Setup logging level
logging.basicConfig(level=logging.DEBUG)

# Setup 'app' variable for GAE
app = dashapp.server

# Read page modules
all_pages = page_loader(["pages", "stdpages"])

dashapp.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@dashapp.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
def display_page(pathname: str) -> html.Div:
    if pathname in all_pages:
        return all_pages[pathname].layout()
    else:
        return '404'


if __name__ == '__main__':
    dashapp.run_server(debug=True)
