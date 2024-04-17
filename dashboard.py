import pandas as pd
import json
import numpy as np
import re

# open shooting data and clean data
def dashboard():
    # make a data frame and analyze it
    df1 = pd.read_csv('Data/shootingData/sd_09_16.csv')
    df2 = pd.read_csv('Data/shootingData/sd_17_24.csv')

    # make a schema for the data frame
    with open('Data/shootingData/sd_09_16_schema.json', 'r') as f:
        sch1 = json.load(f)

    # make a schema for the data frame
    with open('Data/shootingData/sd_17_24_schema.json', 'r') as f:
        sch2 = json.load(f)

    # store the dictionary for data types only
    dict1 = {col: value['dt'] for col, value in sch1.items()}
    dict2 = {col: value['dt'] for col, value in sch2.items()}

    # Drop headers columns
    df_1 = df1[pd.to_numeric(df1['Rk'], errors='coerce').isna()]
    df1 = df1.drop(df_1.index)

    df_2 = df2[pd.to_numeric(df2['Rk'], errors='coerce').isna()]
    df2 = df2.drop(df_2.index)

    # Format numerical values

    ## Compare the schema with the df headers
    for dict, df in zip([dict1, dict2], [df1, df2]):
        sch_ = [i for i in dict.keys()]
        hdrs = [i for i in df.columns]
        comparison_bool = (hdrs == sch_)
        print(f'Data frame and Schema matching: {comparison_bool}')

    # checking all the columns that should be numerical or strings
    int_columns1 = [col for col, value in sch1.items() if value['dt'] == 'int']
    float_columns1 = [col for col, value in sch1.items() if value['dt'] == 'float']

    int_columns2 = [col for col, value in sch2.items() if value['dt'] == 'int']
    float_columns2 = [col for col, value in sch2.items() if value['dt'] == 'float']

    for i_cols, f_cols, df in zip([int_columns1, int_columns2], [float_columns1, float_columns2], [df1, df2]):
        # formatting the numerical values
        df[i_cols] = df[i_cols].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
        df[f_cols] = df[f_cols].apply(pd.to_numeric, errors='coerce').fillna(0.0).astype(float)

    # Combine data in 1 df
    df = pd.concat([df1, df2], axis=0)
    columns_to_keep = ['Rk', 'Player', 'Nation', 'Pos', 'Comp', 'Squad',
                       'Gls', 'SoT', 'SoT%', 'xG', 'npxG', 'G-xG', 'np:G-xG', 'season']

    # Select only the columns you want to keep
    shoot_df = df.loc[:, columns_to_keep]

    tfr_df = pd.read_csv('Data/transferData/trd_2009_2024 .csv', low_memory=False)

    shoot_df['season'] = shoot_df['season'] - 1

    columns_to_keep = ['In', 'Pos', 'Market value', 'previous_team', 'Fee', 'current_team', 'season']
    tfr_df = tfr_df.loc[:, columns_to_keep]

    # renaming the column
    tfr_df.rename(columns={'In': 'Player'}, inplace=True)

    print(tfr_df['season'].unique())
    unvalid_rows = tfr_df[tfr_df['season'] == 'season']
    tfr_df = tfr_df.drop(unvalid_rows.index)

    # make the season as int
    tfr_df['season'] = tfr_df['season'].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
    shoot_df_2023 = shoot_df[shoot_df['season'] == 2023]
    tfr_df_2023 = tfr_df[tfr_df['season'] == 2023]

    tfr_df_2023['Player'] = tfr_df_2023['Player'].apply(lambda x: re.sub(r'(.)\.(.*)', '', x))
    # tfr_df_2023.loc[:, 'Player'] = tfr_df_2023['Player'].apply(lambda x: re.sub(r'(.)\.(.*)', '', x))

    """
    substring = re.findall(pattern, x)[0]
    matches = [match.start() for match in re.finditer(substring, x)]
    
    print(matches)
    x = x[:8]
    print(x)
    """


    def crop(x):
        first_word = x.split()[0]
        second_occ = x[len(first_word):].find(first_word)
        if second_occ != -1:
            x = x[:second_occ + len(first_word)]
        return x


    tfr_df_2023['Player'] = tfr_df_2023.loc[:, 'Player'].apply(lambda x: crop(x))

    tfr_df_2023 = tfr_df_2023.drop_duplicates(subset='Player')

    merged_df = pd.merge(tfr_df_2023, shoot_df_2023, on='Player', how='left')
    merged_df['Fee'].unique()
    pattern = r'^€'
    mask = merged_df['Fee'].str.match(pattern)
    merged_df['Fee'] = merged_df['Fee'].where(mask, other='0')


    def convert_money(money_str):
        if '€' in money_str:
            if 'm' in money_str:
                return float(money_str.replace('€', '').replace('m', '')) * 1000
            elif 'k' in money_str:
                return float(money_str.replace('€', '').replace('k', ''))
        return 0


    merged_df['Fee'] = merged_df.loc[:, 'Fee'].apply(convert_money)
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




