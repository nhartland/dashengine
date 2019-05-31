""" Page for the monitoring of query performance characteristics. """
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


def _query_profile_charts(query: bigquery.BigQueryResult) -> go.Bar:
    return go.Bar(y=['Memory', 'Duration', 'Bytes Processed', 'Bytes Billed'],
                  x=[query.memory_usage(), query.duration, query.bytes_processed, query.bytes_billed],
                  name=query.uuid,
                  orientation='h'
                  )


def _query_profile_table(cached_queries: list):
    TableFields = ["ID", "UUID", "Duration", "Memory Usage", "Bytes Processed", "Bytes Billed"]
    columns = [ {"name": i, "id": i} for i in TableFields]
    data = [{"ID": query.source.query_id,
             "UUID": query.uuid,
             "Duration": query.duration,
             "Memory Usage": query.memory_usage(),
             "Bytes Processed": query.bytes_processed,
             "Bytes Billed": query.bytes_billed} for query in cached_queries]
    return dt.DataTable(id='query-profile-table', columns=columns, data=data,
                        sorting=True, sorting_type="single", row_selectable="single")


@dashapp.callback(
    Output('query-profile-text', 'children'),
    [Input('query-profile-table', 'derived_virtual_data'),
     Input('query-profile-table', 'derived_virtual_selected_rows')])
def get_rows(rows, selected_row_indices):
    if rows is None:
        return "No Query Selected"
    if len(selected_row_indices) != 1:
        return "No Query Selected"
    selected_UUID = rows[selected_row_indices[0]]["UUID"]

    # Fetch cached queries
    queries = bigquery.fetch_cached_queries()
    selected_query = None
    for query in queries:
        if query.uuid == selected_UUID:
            selected_query = query
    if selected_query is None:
        raise RuntimeError(f"Cannot find query with UUID {selected_UUID}")
    query_code = " ``` \n " + selected_query.source.body + " \n ```"
    query_markdown = dcc.Markdown(query_code)

    parameter_table = dt.DataTable(id='query-profile-parameter-table',
            columns=[{"name": "Parameter", "id": "Parameter"}, {"name": "Value", "id": "Value"}],
            data=[{"Parameter": key, "Value": str(value)} for key, value in selected_query.parameters.items()],
            #style_table={'overflowX': 'scroll'},
            style_cell={
                'minWidth': '0px', 'maxWidth': '180px',
                'whiteSpace': 'normal'
            })

    return [query_markdown, parameter_table]


def layout() -> html.Div:
    """ Generates the layout for the query profiling page. """
    # Compute performance metrics
    queries = bigquery.fetch_cached_queries()

    bar_charts = [_query_profile_charts(query) for query in queries]
    layout = go.Layout(barmode='stack', title='Query Profiling')
    profile_figure = go.Figure(data=bar_charts, layout=layout)

    return html.Div(className="container", children=[
        "Note: several of these metrics may return zeroes if the result is returned from cache in BigQuery",
        dcc.Graph(figure=profile_figure),
        _query_profile_table(queries),
        html.Div(id="query-profile-text")
    ])
