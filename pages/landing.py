""" Landing Page for the Dash App. """
import dash_core_components as dcc
import dash_html_components as html

# Default route
ROUTE = "/"
# Name used when linking (for example in the navigation bar)
LINKNAME = "Landing"

with open('README.md', 'r') as readme_file:
    README = readme_file.read()


def layout() -> list:
    return [
        html.Div([
            dcc.Markdown(README)
        ])
    ]
