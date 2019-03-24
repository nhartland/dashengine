import dash
import dash_core_components as dcc
import dash_html_components as html
import bigquery

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dash_app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash_app.server


# Prefetch data for this dashboard
bigquery.prefetch(["githubcommits", "githubcommits2"])
df = bigquery.fetch("githubcommits")


def query_timing_graph():
    """ Generates a graph showing the timings of the cached datasets. """
    query_ids = []
    query_times = []
    for qid, query in bigquery.list().items():
        query_ids.append(qid)
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


def query_memory_graph():
    """ Generates a graph showing the memory (MB) usage of the cached datasets. """
    query_ids = []
    query_memory = []
    for qid, query in bigquery.list().items():
        query_ids.append(qid)
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


dash_app.layout = html.Div(className="container", children=[
    html.H1(children='DashEngine Example'),

    html.Div(children='''
        This is an example of a dashboard on the Dash framework, running on Google App Engine.
    '''),

    html.Div(children=f"Active project used for querying: {bigquery.project_id()}"),
    query_timing_graph(),
    query_memory_graph()
])

if __name__ == '__main__':
    dash_app.run_server(debug=True)
