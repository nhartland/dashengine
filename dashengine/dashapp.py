""" Principle dash app module """
import dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dashapp = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# App.config.suppress_callback_exceptions = True
