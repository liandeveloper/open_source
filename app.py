import streamlit as st
import pandas as pd
import datetime as dt
from datetime import datetime
from library import *

st.set_page_config(
    page_title="GitHub Analytics Dashboard",
    layout="wide",
    page_icon="📊"
)

st.title("🚀 GitHub Analytics Dashboard")
st.markdown("""
Análisis avanzado de repositorios y usuarios de GitHub usando la API.
""")

parse_date = datetime.strptime


usage_data = repo_data.iloc[:, [1, -5, 18, 19, -8, -4, -6, -7, 3, -3, -2]]
usage_data.iloc[:, 1:-3] = usage_data.iloc[:, 1:-3].map(parse_to_list)
usage_data['Main Programming Language'] = usage_data['Main Programming Language'].map(lambda x: x[0] if isinstance(x, list) else x)

tabs = st.tabs(['Find your repo', 'Data Analysis', 'Raw Numbers'])

with tabs[0]:
    st.header('What repo are you looking for?')

    name = st.text_input('Name', placeholder = 'Do you know the name of the repo?')

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    

    with col1:
        cats = st.multiselect('Categories',
            placeholder = "What's  it for?",
            options=extract_unique(usage_data['Category']))
    with col2:
        nat_langs = st.multiselect('Languages available:',
            placeholder = "What language do you speak?",
            options=extract_unique(usage_data['Languages Available']))
    with col3:
        platforms = st.multiselect('Platform',
            placeholder = "What platform is it available on?",
            options=extract_unique(usage_data['Platforms']))
    with col4:
        tecs = st.multiselect('Techniques',
            placeholder = "What techniques does it use?",
            options=extract_unique(usage_data['Techniques used']))
        
    prog_langs = st.multiselect('Programming Languages used:',
            placeholder = "In what language was it written?",
            options=extract_unique(usage_data['Programming Languages used']))
    
    usage_filtered = usage_data.iloc[:, :-3]
    if any([cats, nat_langs, platforms, tecs, prog_langs]):
        if name:
            pass
        if cats:
            usage_filtered = usage_filtered[usage_filtered['Category'].apply(filter(cats))]
        if nat_langs:
            usage_filtered = usage_filtered[usage_filtered['Languages Available'].apply(filter(nat_langs))]
        if platforms:
            usage_filtered = usage_filtered[usage_filtered['Platforms'].apply(filter(platforms))]
        if tecs:
            usage_filtered = usage_filtered[usage_filtered['Techniques used'].apply(filter(tecs))]
        if prog_langs:
            usage_filtered = usage_filtered[usage_filtered['Programming Languages used'].apply(filter(prog_langs))]

    df_event = st.dataframe(usage_filtered, 
                 key = 'repo',
                 hide_index = True, 
                 on_select = 'rerun',
                 selection_mode = 'single-row')
    if df_event.selection['rows']:
        index = df_event.selection['rows'][0]
        name = repo_data.loc[index]['Name']
        current_repo = repo_data[repo_data['Name'] == name]

        with st.expander('REPO DATA'):
            st.header(f'"{name}" repo data')
            col5, col6 = st.columns(2, border=True)
            with col5:
                st.header('Repo Description: ')
                st.subheader('Purpose')
                st.write(current_repo.at[index, 'purpose'])
                st.subheader('Functionality')
                st.write(current_repo.at[index, 'functionality'])
            with col6:
                col7, col8 = st.columns(2)
                with col7:
                    st.subheader('Stars:')
                    st.text(current_repo.at[index, 'stars'])
                    st.subheader('Forks:')
                    st.text(current_repo.at[index, 'forks'])
                    st.subheader('Issues:')
                    st.text(current_repo.at[index, 'open_issues'])
                    st.subheader('Created:')
                    st.text(parse_date(current_repo.at[index, 'created_at'], '%Y-%m-%d').date())
                with col8:
                    st.subheader('Pull Requests:')
                    st.text(current_repo.at[index, 'pull_requests'])
                    st.subheader('Subscribers: ')
                    st.text(current_repo.at[index, 'subscribers_count'])
                    st.subheader('License:')
                    st.text(current_repo.at[index, 'license'])
                    st.subheader('Last Updated:')
                    st.text(current_repo.at[index, 'updated_at'])
            
            st.subheader(f"URL link: {current_repo.at[index, 'url']}") 
    # st.dataframe(repo_data)