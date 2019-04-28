""" Dash Demonstration page for Met Collection data"""
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
# Local
from dashengine.dashapp import dashapp
import dashengine.bigquery as bigquery

# Default route
ROUTE = "/met-demo"
# Name used when linking (for example in the navigation bar)
LINKNAME = "Met Demo"
# Title for rendering in the navbar
TITLE = "Demonstration on Met Data"


def items_by_department() -> go.Figure:
    """ Returns a Graph displaying items per department for the Met."""
    query_data = bigquery.run_query("met-objects-by-department").result
    bar = go.Bar( x=query_data["department"],
                  y=query_data["n_items"])
    layout = go.Layout( title=go.layout.Title(
        text='Item count by department',
        xref='paper',
        x=0
    ))
    return go.Figure(data=[bar], layout=layout)


@dashapp.callback(Output('met-items-by-date', 'figure'),
                  [Input('met-dropdown-filter', 'value')])
def items_by_date(selected_department: str) -> go.Figure:
    """ Histogram of items per date, optionally selecting by department."""
    query_data = bigquery.run_query("met-object-creationdate").result
    # Filter on selected department
    if selected_department is not None:
        query_data = query_data[ query_data["department"] == selected_department]
    hist = go.Histogram( x=query_data["object_begin_date"],
                         xbins=dict(
                         start='1900',
                         end='2000',
                         size='M18'))
    layout = go.Layout( title=go.layout.Title(
        text='Item count by object creation date',
        xref='paper',
        x=0
    ))
    return go.Figure(data=[hist], layout=layout)


def department_dropdown():
    # Dropdown options
    departments = bigquery.run_query("met-objects-by-department").result.department
    return dcc.Dropdown( id="met-dropdown-filter",
                         options=[ {'label': dp, 'value': dp} for dp in departments],
                         placeholder="Filter by department")


def layout() -> html.Div:
    return html.Div(className="container", children=[
        dcc.Graph( figure=items_by_department()),
        dcc.Graph(id="met-items-by-date"),
        department_dropdown()])
