""" Landing Page for the Dash App. """
import dash_core_components as dcc
import dash_html_components as html
import dashengine.bigquery as bigquery

# Default route
ROUTE = "/"

with open('README.md', 'r') as readme_file:
    README = readme_file.read()


def layout() -> html.Div:
    return html.Div(className="container", children=[
        html.Div([
            dcc.Markdown(README)
        ]),
        dcc.Link('Query Profiling', href='/profile')
    ])
