import pandas as pd
import json
import numpy as np
import re
from io import StringIO
import requests

# open shooting data and clean data
def dashboard():
    shooting_url = "https://footballscrapingapi.azurewebsites.net/api/data/shooting"
    tfr_url = "https://footballscrapingapi.azurewebsites.net/api/data/tfr"

    # make data frame from Scraping API
    response = requests.get(shooting_url)
    if response.status_code == 200:
        # Parse the JSON response
        json_data = response.json()
        #print(json_data)
        # Convert the JSON data to a DataFrame
        json_data = StringIO(json_data['data_table'])
        df = pd.read_json(json_data)
    else:
        print("Failed to retrieve data:", response.status_code)
        return

    # make a schema for the data frame
    with open('Data/shootingData/sd_17_24_schema.json', 'r') as f:
        schema = json.load(f)

    # store the dictionary for data types only
    dict = {col: value['dt'] for col, value in schema.items()}

    # Drop headers columns
    _df = df[pd.to_numeric(df['Rk'], errors='coerce').isna()]
    df = df.drop(_df.index)


    # Format numerical values

    ## Compare the schema with the df headers
    sch_ = [i for i in dict.keys()]
    hdrs = [i for i in df.columns]
    comparison_bool = (hdrs == sch_)
    #print(f'Data frame and Schema matching: {comparison_bool}')

    # checking all the columns that should be numerical or strings
    int_columns = [col for col, value in schema.items() if value['dt'] == 'int']
    float_columns = [col for col, value in schema.items() if value['dt'] == 'float']

    for i_cols, f_cols in zip(int_columns, float_columns):
        # formatting the numerical values
        df[i_cols] = df[i_cols].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
        df[f_cols] = df[f_cols].apply(pd.to_numeric, errors='coerce').fillna(0.0).astype(float)

    # Combine data in 1 df
    columns_to_keep = ['Rk', 'Player', 'Nation', 'Pos', 'Comp', 'Squad',
                       'Gls', 'SoT', 'SoT%', 'xG', 'npxG', 'G-xG', 'np:G-xG', 'season']

    # Select only the columns you want to keep
    shoot_df = df.loc[:, columns_to_keep]
    # normalize season column fro both dataframes
    shoot_df['season'] = shoot_df['season'] - 1

    # Process transfers data
    response = requests.get(tfr_url)
    if response.status_code == 200:
        # Parse the JSON response
        json_data = response.json()
        # Convert the JSON data to a DataFrame
        json_data = StringIO(json_data['data_table'])
        tfr_df = pd.read_json(json_data)
    else:
        print("Failed to retrieve data:", response.status_code)
        return

    columns_to_keep = ['In', 'Pos', 'Market value', 'previous_team', 'Fee', 'current_team', 'season']
    tfr_df = tfr_df.loc[:, columns_to_keep]

    # renaming the column
    tfr_df.rename(columns={'In': 'Player'}, inplace=True)

    unvalid_rows = tfr_df[tfr_df['season'] == 'season']
    tfr_df = tfr_df.drop(unvalid_rows.index)

    # make the season as int
    tfr_df['season'] = tfr_df['season'].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
    shoot_df_2023 = shoot_df[shoot_df['season'] == 2023]
    tfr_df_2023 = tfr_df[tfr_df['season'] == 2023]

    tfr_df_2023['Player'] = tfr_df_2023['Player'].apply(lambda x: re.sub(r'(.)\.(.*)', '', x))
    # tfr_df_2023.loc[:, 'Player'] = tfr_df_2023['Player'].apply(lambda x: re.sub(r'(.)\.(.*)', '', x))


    tfr_df_2023['Player'] = tfr_df_2023.loc[:, 'Player'].apply(lambda x: _crop(x))
    tfr_df_2023 = tfr_df_2023.drop_duplicates(subset='Player')

    merged_df = pd.merge(tfr_df_2023, shoot_df_2023, on='Player', how='left')
    merged_df['Fee'].unique()
    pattern = r'^€'
    mask = merged_df['Fee'].str.match(pattern)
    merged_df['Fee'] = merged_df['Fee'].where(mask, other='0')


    merged_df['Fee'] = merged_df.loc[:, 'Fee'].apply(_convert_money)
    merged_df.rename(columns={'Fee': 'Fee in €k'}, inplace=True)
    merged_df.dropna(subset=['Gls'], inplace=True)  # Drop rows with NaN values in specified column
    merged_df = merged_df[merged_df['Gls'] != 0]
    merged_df['Rank'] = (merged_df.loc[:, 'Fee in €k'] / merged_df['Gls']).round(2)
    merged_df = merged_df.sort_values(by='Rank')
    dashboard_df = merged_df[(merged_df['Gls'] > 5) & (merged_df['Rank'] > 0)]
    dashboard_df = dashboard_df.reset_index(drop=True)
    dashboard_df.index += 1
    columns_to_keep = ['Player', 'Pos_x', 'current_team', 'previous_team',
                       'Comp', 'Gls', 'SoT%', 'Market value', 'Fee in €k', 'Rank']

    dashboard_df = dashboard_df[columns_to_keep]
    # Assuming df is your DataFrame
    column_names = {
        'Pos_x': 'Position',
        'current_team': 'Team',
        'previous_team': 'Previous Team',
        'Comp': 'League',
        'Gls': 'Goals',
        'SoT%': 'Shots on Target',
        'Rank': 'Cost per Goal'
    }

    # Rename columns in bulk
    dashboard_df = dashboard_df.rename(columns=column_names)
    dashboard_df = dashboard_df.rename_axis('Rank')

    # Format league names
    league_dict = {
        'it Serie A': 'Sere A (IT)',
        'de Bundesliga': 'Bundesliga (DE)',
        'es La Liga': 'La Liga (ES)',
        'fr Ligue 1': 'Ligue 1 (FR)',
        'eng Premier League': 'Premier League (ENG)'
    }

    dashboard_df['League'] = dashboard_df['League'].replace(league_dict)
    # Reset the index of the DataFrame
    dashboard_df.reset_index(inplace=True)

    # insert the table to the index.html
    html_table = dashboard_df.to_html(index=False)
    start_index = html_table.find('<th>')
    end_index = html_table.find('</tbody>')
    html_table_body = html_table[start_index:end_index]

    # Save the HTML table to a file
    with open('template.html', 'r') as f:
        html_template = f.read()

    html_template = html_template.format(table=html_table_body)

    with open('index.html', 'w') as f:
        f.write(html_template)


def _crop(x):
    first_word = x.split()[0]
    second_occ = x[len(first_word):].find(first_word)
    if second_occ != -1:
        x = x[:second_occ + len(first_word)]
    return x

def _convert_money(money_str):
    if '€' in money_str:
        if 'm' in money_str:
            return float(money_str.replace('€', '').replace('m', '')) * 1000
        elif 'k' in money_str:
            return float(money_str.replace('€', '').replace('k', ''))
    return 0




dashboard()
