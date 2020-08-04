""" Principle dash app module """
import os
import dash
from ruamel.yaml import YAML
from flask_caching import Cache
import dash_bootstrap_components as dbc

# YAML parser
yaml = YAML(typ="safe")

# Configuration
CONFIG_PATH = "config.yaml"
# Setup cache
with open(CONFIG_PATH, "r") as infile:
    CONFIGURATION = yaml.load(infile)

# Setup dash application
dashapp = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0, user-scalable=\"no\""}
    ],
)
dashapp.config.suppress_callback_exceptions = True  # Required as multi-page
dashapp.title = CONFIGURATION["APP_NAME"]

# Setup server secret key for CSRF protection
dashapp.server.secret_key = os.environ.get("SECRET_KEY", "default-secret-key")

# Setup cache according to configuration
cache = Cache(dashapp.server, config=CONFIGURATION["cache-config"])
