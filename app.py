from flask_caching import Cache
import pandas as pd
from dash import Dash, Input, Output, callback
import dash_bootstrap_components as dbc
from dashboard import dashboard
from app_layout import app_layout
from update_dashboard import update_dashboard


# Initializing my Flask app
#server = Flask(__name__)

"""
# Initialize Dash app
app = Dash(__name__, server=server, url_base_pathname='/', )
"""
dashboard_json = 'data/dashboard.json'
dashboard_df = pd.read_json(dashboard_json)


dash_app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash_app.server
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


# Define the app layout
dash_app.layout = app_layout(dashboard_df)
# Callback to update the bar chart and table based on league filter
@callback(
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
"""
@server.route('/refresh_dashboard', methods=['POST'])
def refresh_dashboard():
    global dashboard_df
    # Update the dashboard JSON file
    dashboard()
    dashboard_df = pd.read_json(dashboard_json)
    # Clear the cache
    cache.clear()
    return jsonify({'status': 'success', 'message': 'Dashboard refreshed successfully'})
"""


# Run the app
if __name__ == '__main__':
    print('cache not served')
    #dashboard()
    dash_app.run_server(debug=True, host='0.0.0.0', port='5000')