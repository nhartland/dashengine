""" Landing Page for the Dash App. """
import dash_core_components as dcc
import dash_html_components as html
from dashengine.dataset import DataSet
import dashengine.credentials as credentials


def layout(ds: DataSet) -> html.Div:
    return html.Div(className="container", children=[
        html.H1(children='DashEngine'),

        html.Div(children=f'''
            This is the landing page for the dash application.
            Running in the GCP environment {credentials.project_id()}
        '''),
        dcc.Link('Query Profiling', href='/profile')
    ])
