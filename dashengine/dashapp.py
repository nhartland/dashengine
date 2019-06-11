""" Principle dash app module """
import dash
from ruamel.yaml import YAML
import dash_bootstrap_components as dbc
from flask_caching import Cache

# YAML parser
yaml = YAML(typ="safe")

# Configuration
CONFIG_PATH = "config.yaml"
# Setup cache
with open(CONFIG_PATH, 'r') as infile:
    CONFIGURATION = yaml.load(infile)

# Setup dash application
dashapp = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
dashapp.config.suppress_callback_exceptions = True  # Required as multi-page
dashapp.title = CONFIGURATION["APP_NAME"]

# Setup cache according to configuration
cache = Cache(dashapp.server, config=CONFIGURATION["cache-config"])

