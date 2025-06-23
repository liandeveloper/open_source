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

st.title("🚀 Repo Radar")
st.text("""
This website provides a thorough analysis of the most popular open-source Github repositories.
Skip the search and start buliding with Repo Radar!!!
""")
ss = st.session_state
repo_data = pd.read_csv('repo_data_clean.csv', sep=';')

usage_data = repo_data.iloc[:, [1, -5, 18, 19, -8, -4, -6, -7, 3, -3, -2]]
usage_data.iloc[:, 1:-3] = usage_data.iloc[:, 1:-3].map(parse_to_list)

usage_data['Main Programming Language'] = usage_data['Main Programming Language'].map(lambda x: x[0] if isinstance(x, list) else x)

all_prog_langs = extract_unique(repo_data['Programming Languages used'].map(parse_to_list))

count_langs = lambda column: {key: len(repo_data[repo_data[column].str.contains(key, na = False)]) \
                    for key in all_prog_langs}

tabs = st.tabs(['🔎 Find your repo', '📈 Data Analysis', "🚨 What's next?"])

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
                    st.text(current_repo('License'))
                    st.subheader('Last Updated:')
                    st.text(parse_date(current_repo('updated_at')))
            
            st.subheader(f"URL link: {current_repo('url')}") 
        else:
            st.subheader("Select a Repo to view it's data")
            st.text('You can select a repo by clicking on the checkbox in the first column of the DataFrame')

with tabs[1]:
    st.header("💻 GitHub Analytics Dashboard")
    st.text('Open the sidebar to use our filters')
    st.subheader("📚 Programming Languages Distribution")
    

    # Setting up the dataframes:

    language_count = count_langs('Programming Languages used')
    as_main_language = count_langs('Main Programming Language')

    
    sort_criteria = st.selectbox('Sort by:',
                    options=['Times Used', 'Times Used as Main Language' ],
                    )
    sort_parsed = 'As Main' if sort_criteria == 'Times Used as Main Language' else sort_criteria
    language_count = pd.DataFrame(
                    {'Language':  list(language_count.keys()),
                     'Times Used': list(language_count.values()),
                     'Used %': [num/len(repo_data) for num in language_count.values()],
                     'As Main': list(as_main_language.values()),
                     'As Main %': [num/len(repo_data) for num in as_main_language.values()]
                     }).sort_values(sort_parsed, ascending=False,)

    license_stats = pd.merge(
        pd.DataFrame(repo_data['License'].value_counts()),
        pd.DataFrame(repo_data['License'].value_counts(normalize=True)),
        left_index=True, 
        right_index=True
    ).reset_index()
    license_stats.columns = ['License', 'Count', 'Percent']

    # Filters
    with st.sidebar:
        # chosen_filter = st.selectbox('Choose the type of filter you want to apply:',
        #     options = ['Absolute', 'Relative'],
        # )
        chosen_filter = 'Absolute'
        st.subheader("⚙️ Filters")
        if chosen_filter == 'Absolute':
            min_repos = st.slider(
                "Minimum repositories",
                min_value=1,
                max_value=int(language_count['Times Used'].max()),
                value=15
            )
            max_repos = st.slider(
                "Maximum repositories",
                min_value=min_repos,
                max_value=int(language_count['Times Used'].max()),
                value=int(language_count['Times Used'].max())
            )

            filtered_lang_count = language_count[language_count['Times Used'] >= min_repos]
            filtered_lang_count = filtered_lang_count[filtered_lang_count['Times Used'] <= max_repos]
            
            filtered_licenses = license_stats[license_stats['Count'] >= min_repos]
            filtered_licenses = filtered_licenses[filtered_licenses['Count'] <= max_repos]
        elif chosen_filter == 'Relative':
            pass
    
    col1, col2 = st.columns(2, border=True)

    with col1:
        st.subheader("Frequency Table")
        st.dataframe(
            language_count.style.format({'Used %': '{:.2%}', 'As Main %': '{:.2%}'}),
            use_container_width=True,
            hide_index= True,
        )

    with col2:
        st.subheader("Top Languages")
        top_lang =  st.slider('Amount of languages shown:', 5, 20,12)
        fig = px.bar(
            filtered_lang_count.head(top_lang),
            x='Language',
            y=['Times Used', 'As Main'],
            barmode = 'overlay',
            color='Language',
            text_auto=True,
            hover_name='Language',
            hover_data={
                'Used %': ':.2%', 'As Main %': ':.2%',
                }
        )
        fig.update_traces(
            # texttemplate='%{text:.2%}', 
            textposition='outside',
            showlegend = False
            )
        fig.update_layout(
            xaxis_title="Programming Language",
            yaxis_title="Count",
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("🀄 See More", expanded=False):
        st.subheader('🌲 Tree Map Visualization')
        st.text(f'Viewing and sorting by: {sort_criteria}')
        fig_tree = px.treemap(
                filtered_lang_count,
                names='Language',
                values=sort_parsed,
                path = ['Language', sort_parsed],
                hover_name='Language',
                hover_data={
                    'Times Used': True, 'As Main': True,
                    'Used %': ':.2%', 'As Main %': ':.2%'}
        )
        fig_tree.update_layout(
            height = 400,
            margin = dict(l=0,r=0,b=40,t=0)
        )
        st.plotly_chart(fig_tree, use_container_width=True)
    """ --------------------------------------------------------------------- """

    st.subheader("📜 Software License Distribution")

    fig = px.bar(
        filtered_licenses.sort_values('Count', ascending=True),
        x='Count',
        y='License',
        orientation='h',
        color='Count',
        text='Percent',
        color_continuous_scale='Teal',
        labels={'Count': 'Number of Repos'},
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
    with st.expander("🧩 See More", expanded=False):
        col1, col2 = st.columns(2, border = True)
        with col1:
            st.subheader('📋 Tabular Data')
            st.dataframe(
                filtered_licenses.style.format({'Percent': '{:.2%}'}),
                use_container_width=True,
            )
        with col2:
            st.subheader('🌳 Tree Map Visualization')
            fig_tree = px.treemap(
                filtered_licenses,
                names='License',
                values='Count',
                path = ['License'],
                hover_name='License',
                hover_data={'Percent': ':.2%'},
            )
            fig_tree.update_layout(
                height = 600,
                margin = dict(l=0,r=0,b=40,t=0)
            )
            st.plotly_chart(fig_tree, use_container_width=True)
        

    """ ----------------------------------------------------------------------- """

    st.subheader("🔧 Repo Stats According to License and Language")

    metrics_options = ['Forks', 'Pull Requests', 'Stars', 'Open Issues']    
    parsed_options = [metric.lower().replace(' ', '_') for metric in metrics_options]

    metric_choice = st.multiselect(
        "Select Stats to compare",
        options=metrics_options,
        default=metrics_options[:3],
    )

    parsed_choices = [metric.lower().replace(' ', '_') for metric in metric_choice]

    measurement = st.selectbox('How do you want to group the data',
                    options = ['Mean', 'Median', 'Total'])
    
    if metric_choice:
        big_number = max(repo_data[metric].max() for metric in parsed_options)

        col1, col2 = st.columns(2)
        with col1:
            min_threshold = st.number_input(f"Minimum quantity of {', '.join(parsed_choices)}", 1, big_number, big_number//50, step=1000)
        with col2:
            max_threshold = st.number_input(f"Maximum quantity of {', '.join(parsed_choices)}", 1, big_number, big_number, step=1000)
        
        condition = ((repo_data[parsed_choices] >= min_threshold) & (repo_data[parsed_choices] <= max_threshold)).all(axis=1)
        metrics_df = repo_data[['Main Programming Language', 'License'] + parsed_choices]
        metrics_df = metrics_df[condition]
        if measurement == 'Mean':
            lang_metrics = metrics_df.groupby(['Main Programming Language'], as_index=False)[parsed_choices].mean()
            license_metrics = metrics_df.groupby(['License'], as_index=False)[parsed_choices].mean()
        elif measurement == 'Median':
            lang_metrics = metrics_df.groupby(['Main Programming Language'], as_index=False)[parsed_choices].median()
            license_metrics = metrics_df.groupby(['License'], as_index=False)[parsed_choices].median()
        else:
            license_metrics = lang_metrics = metrics_df

        top_bars = st.slider(
            'Amount of languages/licenses to show:', 
            4, 100, 10)

        col3, col4 = st.columns(2, border=True)
        with col3:
            st.subheader('By Main Language')
            fig = px.bar(
                lang_metrics.sort_values(parsed_choices[0], ascending=False).head(top_bars),
                x='Main Programming Language',
                y=parsed_choices,
                barmode='group',
                color_discrete_sequence=px.colors.qualitative.Pastel,
                labels={'value': 'Count', 'variable': 'Metric', 'Main Programming Language': 'Language'}
            
            )
            fig.update_layout(
                xaxis_title="Programming Language",
                yaxis_title="Count",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            st.subheader('By License')
            fig = px.bar(
                license_metrics.sort_values(parsed_choices[0], ascending=False).head(top_bars),
                x='License',
                y=parsed_choices,
                barmode='group',
                color_discrete_sequence=px.colors.qualitative.Pastel,
                labels={'value': 'Count', 'variable': 'Metric', 'Main Programming Language': 'Language'}
                )
            
            fig.update_layout(
                xaxis_title="License",
                yaxis_title="Count",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("📊 See aggregated data:"):
            agg_df = metrics_df.groupby(['License','Main Programming Language'])[parsed_choices].sum().sort_values(parsed_choices[0], ascending=False)
            
            st.dataframe(
                agg_df.style.background_gradient(cmap='Blues'),
                use_container_width=True
            )
    else:
        st.warning("Please select at least one metric to visualize")

with tabs[2]:
    st.header('We are still not done!!!')
    st.text('''
    We will be upgrading this website soon.
    Stay tuned for more updates.
    ''')

    # quant_1 = st.selectbox('1',
    #     options = ['Stars','Forks', 'Issues', 'Pull Requests']
    #     )
    # quant_2 = st.selectbox('2',
    #     options = ['Stars','Forks', 'Issues', 'Pull Requests'])
    # quali_1 =st.selectbox('3',
    #     options = ['License','Main Programming Language'])
    # qn1_p = 'open_issues' if quant_1 == 'Issues' else quant_1.replace(' ', '_').lower()
    # qn2_p = 'open_issues' if quant_2 == 'Issues' else quant_2.replace(' ', '_').lower()
    # ql1_p = 'License' if quali_1 == 'License' else quali_1

    # st.plotly_chart(px.scatter(
    #     repo_data, 
    #     x=qn1_p, y=qn2_p,
    #     labels = [quant_1, quant_2],
    #     color = ql1_p
    #     )
    #     )
    # st.dataframe(repo_data)

