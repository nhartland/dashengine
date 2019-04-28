""" Page for the monitoring of query performance characteristics. """
# System
import os
# Dash
import dash_core_components as dcc
import dash_html_components as html
# DashEngine
import dashengine.bigquery as bigquery
import dashengine.credentials as credentials

# Route for profiling page
ROUTE = "/profile"

#TODO Add table displaying age of cached queries


def _query_timing_graph() -> dcc.Graph:
    """ Generates a graph showing the timings of the cached datasets. """
    query_ids = []
    query_times = []
    queries = bigquery.list_available_queries()
    for qid in queries:
        query_ids.append(qid)
        query = bigquery.run_query(qid)
        query_times.append(query.duration)

    return dcc.Graph(
        id='time-performance',
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
    queries = bigquery.list_available_queries()
    for qid in queries:
        query_ids.append(qid)
        query = bigquery.run_query(qid)
        memory = query.result.memory_usage(index=True, deep=True).sum()
        query_memory.append(memory/1E6)

    return dcc.Graph(
        id='memory-performance',
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
        html.H1(children='Query Profiling'),

        html.Div(children='''
            Summarised here are the performance characteristics of active queries.
        '''),

        html.Div(children=f"Active project used for querying: {credentials.project_id()}"),
        dcc.Link('Go back to the landing page', href='/'),
        _query_timing_graph(),
        _query_memory_graph()
    ])
