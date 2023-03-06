""" Dash Demonstration page for Met Collection data"""
import plotly.graph_objs as go
from dash import dcc, html
from dash.dependencies import Input, Output

# Local
from dashengine.dashapp import dashapp
import dashengine.bigquery as bigquery

# Default route
ROUTE = "/met-demo"
# Name used when linking (for example in the navigation bar)
LINKNAME = "Met Demo"


def __available_departments() -> list:
    """ Returns a list of all departments in the dataset. """
    return bigquery.run_query("met-objects-by-department").result.department.tolist()


@dashapp.callback(
    Output("met-items-by-department", "figure"), [Input("met-trigger", "children")]
)
def items_by_department(_) -> go.Figure:
    """ Returns a Graph displaying items per department for the Met."""
    query_data = bigquery.run_query("met-objects-by-department").result
    bar = go.Bar(x=query_data["department"], y=query_data["n_items"])
    layout = go.Layout(
        title=go.layout.Title(text="Item count by department", xref="paper", x=0)
    )
    return go.Figure(data=[bar], layout=layout)


@dashapp.callback(
    Output("met-items-by-date", "figure"), [Input("met-dropdown-filter", "value")]
)
def items_by_date(selected_department: str) -> go.Figure:
    """ Histogram of items per date, optionally selecting by department."""
    # Running a BQ parametrised query on creation date and departments
    min_creation_date = 1800

    if selected_department is None:
        # Use list of all departments
        parameters = {
            "creation_date": min_creation_date,
            "departments": __available_departments(),
        }
        query_data = bigquery.run_query("met-object-creationdate", parameters).result
    else:
        # Filter down on a specific department
        parameters = {
            "creation_date": min_creation_date,
            "departments": [selected_department],
        }
        query_data = bigquery.run_query("met-object-creationdate", parameters).result

    # You also have the option to query on all departments and filter in pandas. e.g:
    # query_data = query_data[ query_data["department"] == selected_department]
    # This can be faster than re-querying but requires more RAM

    hist = go.Histogram(
        x=query_data["object_begin_date"],
        xbins=dict(start=str(min_creation_date), end="2000", size="M18"),
    )
    layout = go.Layout(
        title=go.layout.Title(
            text="Item count by object creation date", xref="paper", x=0
        )
    )
    return go.Figure(data=[hist], layout=layout)


@dashapp.callback(
    Output("met-dropdown-filter", "options"), [Input("met-trigger", "children")]
)
def department_dropdown(_):
    # Dropdown options
    departments = __available_departments()
    return [{"label": dp, "value": dp} for dp in departments]


def layout() -> list:
    return [
        # Begin with empty Div: Kicks off callbacks
        html.Div(id="met-trigger", children=[], style={"display": "none"}),
        html.H3(
            "Metropolitain Museum of Art",
            style={"textAlign": "center", "margin-top": "30px"},
        ),
        dcc.Loading(
            id="met-loading",
            children=[
                dcc.Graph(id="met-items-by-department"),
                dcc.Graph(id="met-items-by-date"),
                dcc.Dropdown(
                    id="met-dropdown-filter",
                    value=None,
                    placeholder="Filter by department",
                ),
            ],
            type="graph",
            fullscreen=True,
        ),
    ]
