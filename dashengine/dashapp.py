""" Principle dash app module """
import dash
import dash_bootstrap_components as dbc
from flask_caching import Cache

# Setup dash application
dashapp = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Required by multi-page dash apps
dashapp.config.suppress_callback_exceptions = True

# Setup cache
cache = Cache(dashapp.server, config={
    'CACHE_TYPE': 'simple'
  # 'CACHE_TYPE': 'redis',
  # 'CACHE_REDIS_URL': os.environ.get('REDIS_URL', '')
})
