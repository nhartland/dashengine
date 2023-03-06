""" Landing Page for the Dash App. """
from dash import dcc, html

# Default route
ROUTE = "/"
# Name used when linking (for example in the navigation bar)
LINKNAME = "Landing"

with open("README.md", "r") as readme_file:
    README = readme_file.read()


def layout() -> list:
    return [html.Div([dcc.Markdown(README)])]
