import os
from flask import (Flask, Markup, redirect, render_template, request,
                   send_from_directory, url_for, jsonify)
from flask_caching import Cache
import pandas as pd
from dash import Input, Output, Dash
import dash_bootstrap_components as dbc
from dashboard import dashboard
from app_layout import app_layout
from update_dashboard import update_dashboard


# Initializing my Flask app
server = Flask(__name__)
cache = Cache(server, config={'CACHE_TYPE': 'simple'})

# Initialize Dash app
app = Dash(__name__, server=server, url_base_pathname='/', external_stylesheets=[dbc.themes.BOOTSTRAP])
dashboard_json = 'data/dashboard.json'
dashboard_df = pd.read_json(dashboard_json)


# Define the app layout
app.layout = app_layout(dashboard_df)
# Callback to update the bar chart and table based on league filter
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('data-table', 'data')],
    [Input('league-filter', 'value')]
)
@cache.cached(timeout=3600*4)
def update_layout(selected_league):
    print('Not serving cache')
    fig, data = update_dashboard(selected_league, dashboard_df)
    return fig, data

# Webhook endpoint to refresh the dashboard
@server.route('/refresh-dashboard', methods=['POST'])
def refresh_dashboard():
    global dashboard_df
    # Update the dashboard JSON file
    dashboard()
    dashboard_df = pd.read_json(dashboard_json)
    # Clear the cache
    cache.clear()
    return jsonify({'status': 'success', 'message': 'Dashboard refreshed successfully'})

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)



