""" Page for the monitoring of query performance characteristics. """
import json
# Plotly
import plotly.graph_objs as go
# Dash
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
# DashEngine
from dashengine.dashapp import dashapp
import dashengine.bigquery as bigquery

# Route for profiling page
ROUTE = "/profile"
# Name used when linking, for example in the navigation bar
LINKNAME = "Profiling"
# Title for rendering in the navbar
TITLE = "Cached Query Profiler"


# Helper functions #################################################

def __fetch_query_from_uuid(uuid: str) -> bigquery.BigQueryResult:
    """ Fetches a cached BigQuery result from its UUID.

        Args:
            uuid (str): The UUID of the query to be retrieved.

        Returns:
            (BigQueryResult): The corresponding BigQuery result object.
    """
    # Fetch cached queries
    queries = bigquery.fetch_cached_queries()
    selected_query = None
    for query in queries:
        if query.uuid == uuid:
            # Select a query UUID
            selected_query = query
    if selected_query is None:
        raise RuntimeError(f"Cannot find query with UUID {uuid}")
    return selected_query


def __index_query(query, key: str) -> float:
    """ Returns a property of the query class, keyed by a string.
        The key must be one of:
            ['Memory', 'Duration', 'Bytes Processed', 'Bytes Billed']

        Args:
            query (BigQueryResult): A BigQuery result class
            key (string): A key of the BigQueryResult object

        Returns:
            (float): The value in `query` corresponding to the key.
    """
    ResultDict = {"Memory": query.memory_usage(),
                  "Duration": query.duration,
                  "Bytes Processed": query.bytes_processed,
                  "Bytes Billed": query.bytes_billed}
    return ResultDict[key]


def __normalising_constants(cached_queries: list):
    """ Computes totals over the full set of cached queries to normalise the summary chart. """
    totals = {'Memory': 0.0, 'Duration': 0.0, 'Bytes Processed': 0.0, 'Bytes Billed': 0.0}
    for query in cached_queries:
        for key in totals:
            totals[key] += __index_query(query, key)
    # Avoid dividing by zero
    for key in totals:
        if totals[key] == 0:
            totals[key] = 1
    return totals


# Dash callbacks #################################################

def _query_profile_summary_chart() -> go.Figure:
    """ Generates a set of bar charts for a single query. """
    cached_queries = bigquery.fetch_cached_queries()
    yvals = ['Memory', 'Duration', 'Bytes Processed', 'Bytes Billed']
    totals = __normalising_constants(cached_queries)

    def __bar(query):
        """ Generate a single bar. """
        return go.Bar(y=yvals,
                      x=[ 100 * __index_query(query, key) / totals[key] for key in yvals],
                      name=query.uuid,
                      orientation='h')

    bar_charts = [__bar(query) for query in cached_queries]
    layout = go.Layout(barmode='stack')
    return go.Figure(data=bar_charts, layout=layout)


def _query_profile_table() -> dt.DataTable:
    """ Generates a table profiling all cached queries. """
    cached_queries = bigquery.fetch_cached_queries()
    # Setup all data for the table
    data = [{"ID": query.source.query_id,
             "UUID": query.uuid,
             "Parameters": json.dumps(query.parameters),
             "Duration": query.duration,
             "Memory Usage": query.memory_usage(),
             "Bytes Processed": query.bytes_processed,
             "Bytes Billed": query.bytes_billed} for query in cached_queries]
    hd = {"Parameters": True}  # Hidden data columns
    # Build list of columns from the data keys
    columns = [ {"name": i, "id": i, "hidden": hd.get(i, False)} for i in data[0]]
    # Build datatable
    return dt.DataTable(id='query-profile-table', columns=columns, data=data,
                        sorting=True, sorting_type="single", row_selectable="single",
                        style_header={
                            'backgroundColor': 'white',
                            'fontWeight': 'bold'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': c},
                                'textAlign': 'left'
                            } for c in ['ID', 'UUID']
                        ],
                        style_as_list_view=True)


def _query_profile_body(selected_query) -> dcc.Markdown:
    """ Returns the formatted SQL body of the selected query. """
    # Build query body in markdown code block
    query_code = " ``` \n " + selected_query.source.body + " \n ```"
    return dcc.Markdown(query_code)


def _query_profile_parameters(selected_query):
    """ Returns the parameters of the selected query. """
    parameters = selected_query.parameters
    if len(parameters) == 0:
        return html.H6("No parameters")
    # Build a table consisting of query parameters
    columns = [{"name": "Parameter", "id": "Parameter"},
               {"name": "Value", "id": "Value"}]
    parameter_data = [{"Parameter": key, "Value": str(value)}
                      for key, value in parameters.items()]
    return dt.DataTable(id='query-profile-parameter-table',
                        columns=columns,
                        data=parameter_data,
                        style_table={"margin-bottom": "30px"},
                        style_cell={
                            'minWidth': '0px', 'maxWidth': '180px',
                            'whiteSpace': 'normal'
                        })


def _query_profile_preview(selected_query) -> dt.DataTable:
    """ Returns the formatted SQL body of the selected query. """
    df = selected_query.result.head()
    return dt.DataTable( id='query-profile-preview-table',
                         columns=[{"name": i, "id": i} for i in df.columns],
                         style_table={"margin-bottom": "30px"},
                         data=df.to_dict('records'))


@dashapp.callback(
    Output('query-profile-details', 'children'),
    [Input('query-profile-table', 'derived_virtual_data'),
     Input('query-profile-table', 'derived_virtual_selected_rows')])
def _query_profile_details(rows, selected_row_indices) -> list:
    """ Returns the details (SQL and parameters) of the selected query. """
    if rows is None or len(selected_row_indices) != 1:
        return [html.H5("Select a query to view details",
                        style={"textAlign": "center", "margin-top": "30px"})]
    # Determine selected UUID
    selected_queryID = rows[selected_row_indices[0]]["ID"]
    selected_params  = json.loads(rows[selected_row_indices[0]]["Parameters"])
    selected_query = bigquery.run_query(selected_queryID, selected_params)
    return [ html.H3("Query Details",
                     style={"textAlign": "center", "margin-top": "30px"}),
             html.H4("Query Body",
                     style={"textAlign": "left"}),
             html.Div(children=_query_profile_body(selected_query)),
             html.H4("Query Parameters",
                     style={"textAlign": "left"}),
             html.Div(children=_query_profile_parameters(selected_query)),
             html.H4("Query Preview",
                     style={"textAlign": "left"}),
             html.Div(children=_query_profile_preview(selected_query))]


# Layout #################################################################

def layout() -> html.Div:
    """ Generates the layout for the query profiling page. """
    # No queries cached
    if len(bigquery.fetch_cached_queries()) == 0:
        return html.H4("No queries in cache",
                       style={"textAlign": "center", "margin-top": "30px"})

    return html.Div(className="container", children=[
        dcc.Graph(id="query-profile-summary-chart", figure=_query_profile_summary_chart()),
        html.Div(id="query-profile-table-div", children=_query_profile_table()),
        html.Div(id="query-profile-details")
    ])
