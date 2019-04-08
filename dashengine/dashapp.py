""" Principle dash app module """
import dash
from flask_caching import Cache

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dashapp = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# App-Level cache
dashcache = Cache(dashapp.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'dashengine-cache'
})

# App.config.suppress_callback_exceptions = True
