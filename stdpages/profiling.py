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


def _query_billed_bytes_graph() -> dcc.Graph:
    """ Generates a graph showing the cost in bytes-billed of the cached datasets. """
    query_ids = []
    query_bytes_billed = []
    for query in bigquery.fetch_cached_queries():
        query_ids.append(query.source.name)
        query_bytes_billed.append(query.bytes_billed)

    return dcc.Graph(
        id='profiler-billed-bytes',
        figure={
            'data': [
                {'x': query_ids, 'y': query_bytes_billed, 'type': 'bar'}
            ],
            'layout': {
                'title': 'Query Bytes Billed',
                'yaxis': { 'title': 'Bytes Billed'}
            }
        }
    )


def _query_processed_bytes_graph() -> dcc.Graph:
    """ Generates a graph showing the processed bytes of the cached datasets. """
    query_ids = []
    query_bytes_processed = []
    for query in bigquery.fetch_cached_queries():
        query_ids.append(query.source.name)
        query_bytes_processed.append(query.bytes_billed)

    return dcc.Graph(
        id='profiler-processed-bytes',
        figure={
            'data': [
                {'x': query_ids, 'y': query_bytes_processed, 'type': 'bar'}
            ],
            'layout': {
                'title': 'Query Bytes Processed',
                'yaxis': { 'title': 'Bytes Processed'}
            }
        }
    )


def _query_timing_graph() -> dcc.Graph:
    """ Generates a graph showing the timings of the cached datasets. """
    query_ids = []
    query_times = []
    for query in bigquery.fetch_cached_queries():
        query_ids.append(query.source.name)
        query_times.append(query.duration)

    return dcc.Graph(
        id='profiler-time-performance',
        figure={
            'data': [
                {'x': query_ids, 'y': query_times, 'type': 'bar'}
            ],
            'layout': {
                'title': 'Query Cost (Time)',
                'yaxis': { 'title': 'Query duration (s)'}
            }
        }
    )


def _query_memory_graph() -> dcc.Graph:
    """ Generates a graph showing the memory (MB) usage of the cached datasets. """
    query_ids = []
    query_memory = []
    for query in bigquery.fetch_cached_queries():
        query_ids.append(query.source.name)
        memory = query.result.memory_usage(index=True, deep=True).sum()
        query_memory.append(memory/1E6)

    return dcc.Graph(
        id='profiler-memory-performance',
        figure={
            'data': [
                {'x': query_ids, 'y': query_memory, 'type': 'bar'}
            ],
            'layout': {
                'title': 'Query Cost (Memory)',
                'yaxis': { 'title': 'Memory use (MB)'}
            }
        }
    )


def layout() -> html.Div:
    return html.Div(className="container", children=[
        _query_timing_graph(),
        _query_memory_graph(),
        _query_processed_bytes_graph(),
        _query_billed_bytes_graph()
    ])
