import pandas as pd
import streamlit as st
parse_to_list = lambda x: x.split('//') if isinstance(x, str) else x
extract_unique = lambda series: pd.Series([item for sublist in series\
                if isinstance(sublist, list) for item in sublist]).unique()
filter = lambda options: lambda series: all(f in series for f in options) \
    if isinstance(series, list) else False



repo_data = pd.read_csv('repo_data2.csv', sep = ';')

repo_data = repo_data.rename(columns={
    'name': 'Name',
    'categories': 'Category',
    'topics': 'Github Topics',
    'platforms': 'Platforms',
    'main_prog_language': 'Main Programming Language',
    'programming_languages': 'Programming Languages used',
    'technologies': 'Techniques used',
    'natural_languages': 'Languages Available'
})

repo_data = repo_data.map(lambda x: 'None' if x == None or pd.isna(x) else x)