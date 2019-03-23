import dash
import dash_core_components as dcc
import dash_html_components as html
import concurrent.futures
import bigquery

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dash_app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash_app.server


datasets = ["githubcommits"]
dataset_results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    dataset_jobs = {executor.submit(bigquery.get, dataset): dataset for dataset in datasets}
    for ds_job in concurrent.futures.as_completed(dataset_jobs):
        source = dataset_jobs[ds_job]
        try:
            data = ds_job.result()
            dataset_results[source] = data
        except Exception as exc:
            print('%r generated an exception: %s' % (source, exc))

dash_app.layout = html.Div(className="container", children=[
    html.H1(children='DashEngine Example'),

    html.Div(children='''
        This is an example of a dashboard on the Dash framework, running on Google App Engine.
    '''),

    html.Div(children=f"Active project used for querying: {bigquery.project_id()}"),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])

if __name__ == '__main__':
    dash_app.run_server(debug=True)
