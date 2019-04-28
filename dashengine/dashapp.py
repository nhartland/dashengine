""" Principle dash app module """
import dash
from flask_caching import Cache
import dash_bootstrap_components as dbc

dashapp = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App-Level cache
dashcache = Cache(dashapp.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'dashengine-cache'
})

dashapp.config.suppress_callback_exceptions = True
