import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import os, datetime, time
from datetime import datetime as dt
from github import Github
from my_library import repos_df, usage_df


st.set_page_config(
    page_title="GitHub Analytics Dashboard",
    layout="wide",
    page_icon="📊"
)

st.title("🚀 GitHub Analytics Dashboard")
st.markdown("""
Análisis avanzado de repositorios y usuarios de GitHub usando la API.
""")


@st.cache_data
def load_data():
    return repos_df, usage_df

repos_df, usage_df = load_data()

tab1, tab2, tab3 = st.tabs(['Languages and licenses', 'Usage', 'Tab3'])

with tab1:
    st.header("📚 Distribución de Lenguajes de Programación")

    language_count = pd.merge(
        pd.DataFrame(repos_df['language'].value_counts()), 
        pd.DataFrame(repos_df['language'].value_counts(normalize=True)),
        left_index=True, 
        right_index=True
    ).reset_index()
    language_count.columns = ['Lenguaje', 'Conteo', 'Porcentaje']

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Tabla de Frecuencia")
        st.dataframe(
            language_count.style.format({'Porcentaje': '{:.2%}'}),
            use_container_width=True,
            height=400
        )

    with col2:
        st.subheader("Top Lenguajes")
        fig = px.bar(
            language_count.head(10),
            x='Lenguaje',
            y='Conteo',
            color='Lenguaje',
            text='Porcentaje',
            labels={'Conteo': 'N° de Repositorios', 'Porcentaje': '%'},
            hover_data={'Porcentaje': ':.2%'}
        )
        fig.update_traces(texttemplate='%{text:.2%}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    """ --------------------------------------------------------------------- """

    st.header("📜 Distribución de Licencias de Software")

    license_stats = pd.merge(
        pd.DataFrame(repos_df['license'].value_counts()),
        pd.DataFrame(repos_df['license'].value_counts(normalize=True)),
        left_index=True, 
        right_index=True
    ).reset_index()
    license_stats.columns = ['Licencia', 'Conteo', 'Porcentaje']

    st.subheader("⚙️ Filtros")
    min_repos = st.slider(
        "Mínimo de repositorios:",
        min_value=1,
        max_value=int(license_stats['Conteo'].max()),
        value=5
    )
    show_unknown = st.checkbox("Mostrar licencias no especificadas", True)

    filtered_licenses = license_stats[license_stats['Conteo'] >= min_repos]
    if not show_unknown:
        filtered_licenses = filtered_licenses[~filtered_licenses['Licencia'].str.contains('None', na=True)]

    fig = px.bar(
        filtered_licenses.sort_values('Conteo', ascending=True),
        x='Conteo',
        y='Licencia',
        orientation='h',
        color='Conteo',
        text='Porcentaje',
        color_continuous_scale='Teal',
        labels={'Conteo': 'N° Repositorios'},
        hover_data={'Porcentaje': ':.2%'}
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

    with st.expander("📋 Ver datos tabulares", expanded=False):
        st.dataframe(
            filtered_licenses.style.format({'Porcentaje': '{:.2%}'}),
            height=300,
            use_container_width=True
        )

    with st.expander("🧩 Ver distribución porcentual", expanded=False):
        fig_pie = px.pie(
            filtered_licenses,
            names='Licencia',
            values='Conteo',
            hole=0.3,
            hover_data=['Porcentaje']
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

    biggest_languages = language_count[language_count['Conteo'] >= lang_threshold]
    biggest_licenses = license_stats[license_stats['Conteo'] >= license_threshold]

    clean_df = repos_df.copy()
    clean_df['language'] = clean_df['language'].apply(
        lambda x: 'Other' if x not in biggest_languages['Lenguaje'].values else x
    )
    clean_df['license'] = clean_df['license'].apply(
        lambda x: 'Other' if x not in biggest_licenses['Licencia'].values else x
    )

    # st.subheader("Comparación de Forks y Pull Requests por Lenguaje")

    metric_choice = st.multiselect(
        "Selecciona métricas a comparar:",
        options=['forks', 'pull_requests', 'open_issues'],
        default=['forks', 'pull_requests']
    )

    if len(metric_choice) >= 2:
        fig = px.bar(
            clean_df.sort_values('forks', ascending=False),
            x='language',
            y=metric_choice,
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={'value': 'Count', 'variable': 'Metric', 'language': 'Language'},
            hover_data=['license']
        )
        fig.update_layout(
            xaxis_title="Lenguaje de Programación",
            yaxis_title="Cantidad",
            hovermode="x unified"
        )
        st.plotly_chart(fig)
        

        with st.expander("📊 Ver datos agregados"):
            agg_df = clean_df.groupby('language')[metric_choice].sum().sort_values(metric_choice[0], ascending=False)
            st.dataframe(
                agg_df.style.background_gradient(cmap='Blues'),
                use_container_width=True
            )
    else:
        st.warning("Por favor selecciona al menos dos métricas para visualizar")

    st.subheader("Distribución por Licencia")
    license_metric = st.selectbox(
        "Métrica para análisis de licencias:",
        options=['forks', 'pull_requests', 'watchers_count']
    )

    if license_metric:
        license_fig = px.box(
            clean_df,
            x='license',
            y=license_metric,
            color='license',
            points="all",
            hover_data=['name']
        )
        license_fig.update_layout(
            xaxis_title="Tipo de Licencia",
            yaxis_title=license_metric.replace('_', ' ').title(),
            showlegend=False
        )
        st.plotly_chart(license_fig, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        cats = st.multiselect('Categories',
            options=['a'])
    with col2:
        nat_langs = st.multiselect('Language:',
            options=['python'])
    with col3:
        platforms = st.multiselect('Platform',
            options=['a'])
    with col4:
        tecs = st.multiselect('Technologies',
            options=['a'])
    prog_langs = st.multiselect('edited_df Languages:',
            options=['python', 'javascript'])
    
    edited_df = usage_df[usage_df['programming_languages'] == str('//'.join(prog_langs))].map(lambda x: x.split('//') if isinstance(x, str) else x)
    if any([cats, nat_langs, prog_langs, tecs, platforms]):
        event = st.dataframe(data=edited_df.iloc[:, 1: -4], on_select='rerun')
    else:
        event = st.dataframe(data=usage_df.map(lambda x: x.split('//') if isinstance(x, str) else x).iloc[:, 1: -4], on_select='rerun') 
    
    if event.selection:
        st.header()
        st.header('Purpose')
        st.write(edited_df.iloc[event.selection['rows'][-1]]['purpose'][0])

        st.header('Functionality')
        st.write(edited_df.iloc[event.selection['rows'][-1]]['functionality'][0])
    

with tab3:
    pass