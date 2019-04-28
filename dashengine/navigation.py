# System
import pkgutil
import importlib
import logging
# Dash
import dash_bootstrap_components as dbc


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


# Build navigation bar
def navigation_bar(pages: dict) -> dbc.NavbarSimple:
    """ Builds the navigation bar for the dashboards. """
    return dbc.NavbarSimple(
        children=[
            # dbc.NavItem(dbc.NavLink("Link", href="#")), # Additional link example
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Navigation",
                children=[
                    dbc.DropdownMenuItem(mod.LINKNAME, href=mod.ROUTE) for mod in pages.values()
                ],
            ),
        ],
        brand="DashEngine",
        brand_href="/",
        sticky="top",
    )
