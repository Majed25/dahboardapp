import os
from flask_caching import Cache
import pandas as pd
from dash import Dash, Input, Output, callback
import dash_bootstrap_components as dbc
from dashboard import dashboard
from app_layout import app_layout
from update_dashboard import update_dashboard
import json
from datetime import datetime

# Run the Dahsboard funciton to generate data and create my df
dashboard()
dashboard_json= 'data/dashboard.json'
dashboard_df = pd.read_json(dashboard_json)
last_refreshed = datetime.now().strftime('%Y-%m-%d %H:%M')

# Initialize Dash app
dash_app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash_app.server

# Configure Caching
cache = Cache(app, config={
    # try 'filesystem' if you don't want to setup redis
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': os.environ.get('filesystem', 'data/cache')
})
app.config.suppress_callback_exceptions = True

# Define the app layout
dash_app.layout = app_layout(dashboard_df)

# Callback to update the bar chart and table based on league filter
@callback(
    [Output('bar-chart', 'figure'),
     Output('data-table', 'data'),
    Output('last-refreshed', 'children')],
    [Input('league-filter', 'value')]
)
@cache.memoize(timeout=3600*4)  # in seconds
def update_layout(selected_league):
    print('No cache callbacks')
    fig, data = update_dashboard(selected_league, dashboard_df)
    global last_refreshed
    timestamp = f'Last refreshed: {last_refreshed}'
    return fig, data, timestamp

# Webhook endpoint to refresh the dashboard
@app.route('/refresh_dashboard', methods=['POST'])
def refresh_dashboard():
    global dashboard_df
    global last_refreshed
    # Update the dashboard JSON file
    dashboard()
    print('refreshed')
    dashboard_df = pd.read_json(dashboard_json)
    #Clear the cache
    cache.clear()
    print('cleared')
    last_refreshed = datetime.now().strftime('%Y-%m-%d %H:%M')
    return json.dumps({'status': 'success', 'message': 'Dashboard refreshed successfully'})


# Run the app
if __name__ == '__main__':
    cache.clear()
    dash_app.run_server(debug=True, host='0.0.0.0', port='5000')