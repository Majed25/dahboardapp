import plotly.express as px

def update_dashboard(selected_league, dashboard_df):
    if selected_league == 'All Leagues':
        filtered_df = dashboard_df
    else:
        filtered_df = dashboard_df[dashboard_df['League'] == selected_league]

    # Sort the DataFrame by 'Cost per Goal' in ascending order
    sorted_df = filtered_df.sort_values(by='Cost per Goal', ascending=False)

    fig = px.bar(sorted_df, x='Player', y='Cost per Goal', color='League',
                 title='Filter by clicking on the League Color',
                 hover_data=['League'])
    fig.update_yaxes(range=[0, dashboard_df['Cost per Goal'].max() * 1.2])  # Extend y-axis to make bars longer

    return fig, filtered_df.to_dict('records')