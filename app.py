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
import logging


# configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")



# Run the Dahsboard funciton to generate data and create my df
dashboard_df, last_refreshed = None, None

def generate_data(file):
    try:
        dashboard_df = pd.read_json(file)
        return dashboard_df
    except Exception as e:
        app.logger.info(f'Error loading file: {e}')


# Initialize Dash app
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.logger.info('Starting App')

# Configure Cache
cache_dir = os.environ.get('filesystem', 'data/cache')
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
cache = Cache(server, config={
    # try 'filesystem' if you don't want to setup redis
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': cache_dir
})
app.config.suppress_callback_exceptions = True

# Define the app layout
def def_layout(app):
    try:
        app.layout = app_layout(generate_data('data/dashboard.json'))
    except Exception as e:
        app.logger.info(f'Error setting up app layout: {e}')

# Callback to update the bar chart and table based on league filter
@callback(
    [Output('bar-chart', 'figure'),
     Output('data-table', 'data'),
    Output('last-refreshed', 'children')],
    [Input('league-filter', 'value')]
)
@cache.memoize(timeout=3600*4)
# in seconds
def update_layout(selected_league):
    app.logger.info('Update filters')
    global last_refreshed
    app.logger.info('No cache Served')
    fig, data = update_dashboard(selected_league, generate_data('data/dashboard.json'))
    timestamp = f'Last refreshed: {last_refreshed}'
    return fig, data, timestamp

# Webhook endpoint to refresh the dashboard
@server.route('/refresh_dashboard', methods=['POST'])
def refresh_dashboard():
    global dashboard_df, last_refreshed
    # Update the dashboard JSON file
    try:
        dashboard()
        app.logger.info('Dashboard refreshed')
        dashboard_df = generate_data('data/dashboard.json')
        last_refreshed = datetime.now().strftime('%Y-%m-%d %H:%M')
        #Clear the cache
        cache.clear()
        print('cleared')
        return json.dumps({'status': 'success', 'message': 'Dashboard refreshed successfully'})
    except Exception as e:
        app.logger.error('Error when refreshing dahsboard: {e}')


# Run the app
if __name__ == '__main__':
    logging.info('Start app')
    dashboard()
    last_refreshed = datetime.now().strftime('%Y-%m-%d %H:%M')
    #clear cache
    logging.info('Clear previous cache')
    cache.clear()
    def_layout(app)
    app.run_server(host='0.0.0.0')