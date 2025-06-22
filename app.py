import streamlit as st
import pandas as pd
import plotly.express as px
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
This website provides a thorough analysis of the most popular open-source Github repositories
""")

ss = st.session_state
repo_data = pd.read_csv('repo_data_clean.csv', sep=';')

usage_data = repo_data.iloc[:, [1, -5, 18, 19, -8, -4, -6, -7, 3, -3, -2]]
usage_data.iloc[:, 1:-3] = usage_data.iloc[:, 1:-3].map(parse_to_list)

usage_data['Main Programming Language'] = usage_data['Main Programming Language'].map(lambda x: x[0] if isinstance(x, list) else x)

tabs = st.tabs(['Find your repo', 'Data Analysis', 'Raw Data'])

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
    
    usage_filtered = usage_data
    if any([name, cats, nat_langs, platforms, tecs, prog_langs]):
        if name:
            usage_filtered = usage_filtered[usage_filtered['Name'].str.contains(name.strip('\\'), case = False, na = False)]
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

    df_event = st.dataframe(usage_filtered.iloc[:, :-3], 
                 key = 'repo',
                 hide_index = True, 
                 on_select = 'rerun',
                 selection_mode = 'single-row')
    

    with st.expander('REPO DATA', expanded = True):
        if df_event.selection['rows']:
            index = df_event.selection['rows'][0]
            repo_name = usage_filtered.iloc[index]['Name']
            current_repo = lambda column: repo_data.loc[repo_data['Name'] == repo_name, column].values[0]
            st.header(f'"{repo_name}" repo data')
            col5, col6 = st.columns(2, border=True)
            with col5:
                st.header('Repo Description: ')
                st.subheader('Purpose')
                st.write(current_repo('purpose'))
                st.subheader('Functionality')
                st.write(current_repo('functionality'))
            with col6:
                col7, col8 = st.columns(2)
                with col7:
                    st.subheader('Stars:')
                    st.text(current_repo('stars'))
                    st.subheader('Forks:')
                    st.text(current_repo('forks'))
                    st.subheader('Issues:')
                    st.text(current_repo('open_issues'))
                    st.subheader('Created:')
                    st.text(parse_date(current_repo('created_at')))
                with col8:
                    st.subheader('Pull Requests:')
                    st.text(current_repo('pull_requests'))
                    st.subheader('Subscribers: ')
                    st.text(current_repo('subscribers_count'))
                    st.subheader('License:')
                    st.text(current_repo('license'))
                    st.subheader('Last Updated:')
                    st.text(parse_date(current_repo('updated_at')))
            
            st.subheader(f"URL link: {current_repo('url')}") 
        else:
            st.subheader("Select a Repo to view it's data")
            st.text('You can select a repo by clicking on the checkbox in the first column')

with tabs[1]:
    st.header("📚 Programming Languages Distribution")

    language_count = count_langs('Programming Languages used')
    as_main_language = count_langs('Main Programming Language')

    language_count = pd.DataFrame(
                    {'Language':  list(language_count.keys()),
                     'Times Used': list(language_count.values()),
                     'Used %': [num/len(repo_data) for num in language_count.values()],
                     'As Main': list(as_main_language.values()),
                     'As Main %': [num/len(repo_data) for num in as_main_language.values()]
                     }).sort_values('Times Used', ascending=False,)

    filtered_lang_count = language_count
    min_repos = 0
    max_repos = len(repo_data)
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Frequency Table")
        st.dataframe(
            language_count.style.format({'Used %': '{:.2%}', 'As Main %': '{:.2%}'}),
            use_container_width=True,
            hide_index= True,
        )

    with col2:
        st.subheader("Top Lenguajes")
        fig = px.bar(
            filtered_lang_count.head(15),
            x='Language',
            y=['Times Used', 'As Main'],
            barmode = 'overlay',
            color='Language',
            text= 'Used %',
            labels={'Conteo': 'N° de Repositorios', 'Porcentaje': '%'},
            hover_data={
                'Used %': ':.2%', 'As Main %': ':.2%'}
        )
        fig.update_traces(texttemplate='%{text:.2%}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    """ --------------------------------------------------------------------- """

    st.header("📜 Software License Distribution")

    license_stats = pd.merge(
        pd.DataFrame(repo_data['license'].value_counts()),
        pd.DataFrame(repo_data['license'].value_counts(normalize=True)),
        left_index=True, 
        right_index=True
    ).reset_index()
    license_stats.columns = ['License', 'Count', 'Percent']

    show_unknown = st.checkbox("Mostrar licencias no especificadas", True)

    filtered_licenses = license_stats[license_stats['Count'] >= min_repos]
    filtered_licenses = filtered_licenses[filtered_licenses['Count'] <= max_repos]
    
    if not show_unknown:
        filtered_licenses = filtered_licenses[~filtered_licenses['License'].str.contains('None', na=True)]

    fig = px.bar(
        filtered_licenses.sort_values('Count', ascending=True),
        x='Count',
        y='License',
        orientation='h',
        color='Count',
        text='Percent',
        color_continuous_scale='Teal',
        labels={'Count': 'N° Repositorios'},
        hover_data={'Percent': ':.2%'}
    )
    fig.update_traces(
        texttemplate='%{text:.2%}', 
        textposition='outside'
    )
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    filtered_licenses
    with st.expander("📋 See More", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            filtered_licenses
            st.dataframe(
                filtered_licenses.style.format({'Percent': '{:.2%}'}),
                use_container_width=True
            )
        with col2:
            fig_pie = px.pie(
                filtered_licenses,
                names='License',
                values='Count',
                hole=0.3,
                hover_data=['Percent']
            )
            fig_pie.update_traces(
                textinfo='percent+label',
                pull=[0.1 if i == 0 else 0 for i in range(len(filtered_licenses))]
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        

    """ ----------------------------------------------------------------------- """

    st.header("🔧 Análisis Agrupado de Lenguajes y Licencias")

    col1, col2 = st.columns(2)
    with col1:
        lang_threshold = st.slider("Umbral mínimo para lenguajes", 1, 50, 12)
    with col2:
        license_threshold = st.slider("Umbral mínimo para licencias", 1, 100, 40)

    biggest_languages = language_count[language_count['Times Used'] >= lang_threshold]
    biggest_licenses = license_stats[license_stats['Count'] >= license_threshold]

    clean_df = repo_data.copy()
    clean_df['Main Programming Language'] = clean_df['Main Programming Language'].apply(
        lambda x: 'Other' if x not in biggest_languages['Language'].values else x
    )
    clean_df['license'] = clean_df['license'].apply(
        lambda x: 'Other' if x not in biggest_licenses['License'].values else x
    )

    st.subheader("Comparación de Forks y Pull Requests por Lenguaje")

    metric_choice = st.multiselect(
        "Selecciona métricas a comparar:",
        options=['forks', 'pull_requests', 'open_issues', 'stars'],
        default=['forks', 'pull_requests']
    )

    if metric_choice:
        fig = px.bar(
            clean_df.sort_values('forks', ascending=False),
            x='Main Programming Language',
            y=metric_choice,
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={'value': 'Count', 'variable': 'Metric', 'Main Programming Language': 'Language'},
        
        )
        fig.update_layout(
            xaxis_title="Lenguaje de Programación",
            yaxis_title="Cantidad",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
        

        with st.expander("📊 Ver datos agregados"):
            agg_df = clean_df.groupby('Main Programming Language')[metric_choice].sum().sort_values(metric_choice[0], ascending=False)
            st.dataframe(
                agg_df.style.background_gradient(cmap='Blues'),
                use_container_width=True
            )
    else:
        st.warning("Por favor selecciona al menos una métrica para visualizar")

with tabs[2]:
    quant_1 = st.selectbox('1',
        options = ['Stars','Forks', 'Issues', 'Pull Requests']
        )
    quant_2 = st.selectbox('2',
        options = ['Stars','Forks', 'Issues', 'Pull Requests'])
    quali_1 =st.selectbox('3',
        options = ['License','Main Programming Language'])
    qn1_p = 'open_issues' if quant_1 == 'Issues' else quant_1.replace(' ', '_').lower()
    qn2_p = 'open_issues' if quant_2 == 'Issues' else quant_2.replace(' ', '_').lower()
    ql1_p = 'license' if quali_1 == 'License' else quali_1

    st.plotly_chart(px.scatter(
        repo_data, 
        x=qn1_p, y=qn2_p,
        labels = [quant_1, quant_2],
        color = ql1_p
        )
        )
    st.dataframe(repo_data)

with st.sidebar:
    chosen_filter = st.selectbox('Choose the type of filter you want to apply:',
        options = ['Absolute', 'Percentage'],
    )
    st.subheader("⚙️ Filtros")
    if chosen_filter == 'Absolute':
        min_repos = st.slider(
            "Mínimo de repositorios:",
            min_value=1,
            max_value=int(language_count['Times Used'].max()),
            value=1
        )
        max_repos = st.slider(
            "Maximo de repositorios:",
            min_value=min_repos,
            max_value=int(language_count['Times Used'].max()),
            value=int(language_count['Times Used'].max())
        )

        filtered_lang_count = language_count[language_count['Times Used'] >= min_repos]
        filtered_lang_count = filtered_lang_count[filtered_lang_count['Times Used'] <= max_repos]