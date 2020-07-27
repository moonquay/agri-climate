"""Functions for project data."""

# %matplotlib inline
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import requests
import urllib.request
from bs4 import BeautifulSoup
import re
import time

plt.style.use('seaborn-whitegrid')


def import_ag_data(data_csv):
    """Imports and cleans up ag-survey csv file"""
    df = pd.read_csv(data_csv)
    col_to_drop = ['Program', 'Period', 'Week Ending', 'Geo Level', 'State',
                   'State ANSI', 'Zip Code', 'Region', 'watershed_code',
                   'Watershed', 'Data Item', 'Domain', 'Domain Category',
                   'Ag District', 'Ag District Code', 'CV (%)']
    df = df.drop(col_to_drop, axis=1)
    df = df[(df['Value'] != ' (D)') & (df['Value'] != ' (Z)')]
    df = df.replace(to_replace=r',', value='', regex=True)
    df['Value'] = df['Value'].astype('int')
    df = df.rename(columns={'Value': 'Yield'})
    df['Year'] = pd.to_datetime(df['Year'], format='%Y')
    return df


def import_precip_data(counties):
    """Web scraping of precipitation data"""
    for index, row in counties.iterrows():
        station = row[2]
        url = f'https://wrcc.dri.edu/WRCCWrappers.py?sodxtrmts+0{station}+por+por+pcpn+none+msum+5+01+F'
        result = requests.get(url)
        soup = BeautifulSoup(result.text, 'html.parser')
        table = soup.find('table')
        data = pd.read_html(str(table))
        df = data[0]
        df.columns = df.iloc[0]
        df = df.drop([0])
        df = df.iloc[-65:-8, :]
        df = df.rename(columns={'YEAR(S)': 'Year'})
        df['Year'] = pd.to_datetime(df['Year'], format='%Y')
        df = df.set_index('Year')
        df = df.dropna(axis=1)
        df = df.replace(to_replace='-----', value=np.nan)
        df = df.astype('float64')
        df = df.fillna(df.mean().round(2))
        df = df.add_suffix('_p')
        name = row[0]
        df['County'] = name
        df.to_csv(f'{name}_precip.csv')
        print(f'Precipitation data from {name} saved')
    time.sleep(3.14)
    print('Done')


def import_temp_data(counties):
    """Web scraping of maximum temperature data"""
    for index, row in counties.iterrows():
        station = row[2]
        url = f'https://wrcc.dri.edu/WRCCWrappers.py?sodxtrmts+0{station}+por+por+maxt+none+mave+5+01+F'
        result = requests.get(url)
        soup = BeautifulSoup(result.text, 'html.parser')
        table = soup.find('table')
        data = pd.read_html(str(table))
        df = data[0]
        df.columns = df.iloc[0]
        df = df.drop([0])
        df = df.iloc[-65:-8, :]
        df = df.rename(columns={'YEAR(S)': 'Year'})
        df['Year'] = pd.to_datetime(df['Year'], format='%Y')
        df = df.set_index('Year')
        df = df.dropna(axis=1)
        df = df.replace(to_replace='-----', value=np.nan)
        df = df.astype('float64')
        df = df.fillna(df.mean().round(2))
        df = df.add_suffix('_t')
        name = row[0]
        df['County'] = name
        df.to_csv(f'{name}_avgmaxtemp.csv')
        print(f'Avg. max. temp. data from {name} saved')
    time.sleep(3.14)
    print('Done')
