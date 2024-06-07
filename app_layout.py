from dash import  dcc, html, dash_table
import dash_bootstrap_components as dbc

def app_layout(dashboard_df):
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1(children='Football Transfer Dashboard', className='mt-4 mb-4'))),
        dbc.Row(dbc.Col(dcc.Dropdown(
            id='league-filter',
            options=[{'label': 'All Leagues', 'value': 'All Leagues'}] + [{'label': league, 'value': league} for league in dashboard_df['League'].unique()],
            value='All Leagues',
            clearable=False,
            placeholder='Select a league'
        ))),

        dbc.Row(dbc.Col(html.H2(children='Most Important Transfer Deals Based on Cost per Goal Scored', className='mt-4'))),

        dbc.Row(dbc.Col(dcc.Graph(
            id='bar-chart',
            style={'height': '850px'}
        ))),

        dbc.Row(dbc.Col(html.H2(children='Detailed Transfer Deal Information', className='mt-4'))),

        dbc.Row(dbc.Col(dash_table.DataTable(
            id='data-table',
            columns=[{"name": i, "id": i} for i in dashboard_df.columns],
            style_table={'overflowX': 'auto', 'marginBottom': '20px'},
            style_as_list_view=True,
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'color': 'black',
                'fontWeight': 'bold'
            },
            style_cell={
                'height': 'auto',
                'minWidth': '0px', 'maxWidth': '180px',
                'whiteSpace': 'normal',
                'backgroundColor': 'rgb(255, 255, 255)',
                'color': 'black'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(245, 245, 245)'
                },
                {
                    'if': {'row_index': 'even'},
                    'backgroundColor': 'rgb(255, 255, 255)'
                },
                {
                    'if': {'state': 'active'},
                    'backgroundColor': 'rgb(240, 240, 240)',
                    'border': '1px solid rgb(200, 200, 200)'
                },
                {
                    'if': {'state': 'selected'},
                    'backgroundColor': 'rgb(200, 230, 255)',
                    'border': '1px solid rgb(200, 200, 200)'
                }
            ]
        ))),

    ])

