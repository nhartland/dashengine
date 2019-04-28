""" Landing Page for the Dash App. """
import dash_core_components as dcc
import dash_html_components as html
import dashengine.bigquery as bigquery

# Default route
ROUTE = "/"


def layout() -> html.Div:
    return html.Div(className="container", children=[
        html.H1(children='DashEngine'),

        html.Div(children=f'''
            This is the landing page for the dash application.
            Running in the GCP environment {bigquery.PROJECT_ID}
        '''),
        dcc.Link('Query Profiling', href='/profile')
    ])
