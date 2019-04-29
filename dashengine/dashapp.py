""" Principle dash app module """
import dash
import dash_bootstrap_components as dbc

dashapp = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
dashapp.config.suppress_callback_exceptions = True
