""" Page for the monitoring of query performance characteristics. """
# Dash
import dash_core_components as dcc
import dash_html_components as html
# DashEngine
import dashengine.bigquery as bigquery

# Route for profiling page
ROUTE = "/profile"
# Name used when linking, for example in the navigation bar
LINKNAME = "Profiling"
# Title for rendering in the navbar
TITLE = "Cached Query Profiler"


def _query_profile_chart(gid: str, title: str, ylabel: str,
                         xvalues: list, yvalues: list)  -> dcc.Graph:
    """ Generates a bar chart showing a performance metric upon the cached datasets.

    Args:
        gid (str): A dash string identifier for the chart.
        title (str): The title of the generated chart.
        ylabel (str): The y-axis label of the generated chart.
        xvalues (list): A list of the x-values in the bar chart.
        yvalues (list): A list of the y-values in the bar chart.

    Returns:
        (dcc.Graph): A generated bar chart based upon the input arguments.
    """
    return dcc.Graph(
        id=gid,
        figure={
            'data': [
                {'x': xvalues, 'y': yvalues, 'type': 'bar'}
            ],
            'layout': {
                'title': title,
                'yaxis': { 'title': ylabel}
            }
        }
    )


def layout() -> html.Div:
    """ Generates the layout for the query profiling page. """
    # Compute performance metrics
    queries = bigquery.fetch_cached_queries()
    query_ids             = [query.source.name           for query in queries]
    query_duration        = [query.duration              for query in queries]
    query_bytes_processed = [query.bytes_processed / 1E6 for query in queries]
    query_bytes_billed    = [query.bytes_billed / 1E6    for query in queries]
    query_memory          = [query.memory_usage()        for query in queries]

    return html.Div(className="container", children=[
        "Note: several of these metrics may return zeroes if the result is returned from cache in BigQuery",
        _query_profile_chart('profiler-memory-performance', 'Memory Usage', 'Memory use (MB)',
                             query_ids, query_memory),
        _query_profile_chart('profiler-time-performance', 'Query Duration', 'Duration (s)',
                             query_ids, query_duration),
        _query_profile_chart('profiler-bytes-processed', 'Processed Data ', 'Processed Data (MB)',
                             query_ids, query_bytes_processed),
        _query_profile_chart('profiler-bytes-billed', 'Billed Data', 'Billed Data (MB)',
                             query_ids, query_bytes_billed)
    ])
