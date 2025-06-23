import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from my_library import repos_df, users_df

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
    return repos_df

repos_df = load_data()

""" --------------------------------------------------------------------- """

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

# Análisis de Licencias - Versión Compacta
st.header("📜 Distribución de Licencias de Software")

# 1. Procesamiento de datos
license_stats = pd.merge(
    pd.DataFrame(repos_df['License'].value_counts()),
    pd.DataFrame(repos_df['License'].value_counts(normalize=True)),
    left_index=True, 
    right_index=True
).reset_index()
license_stats.columns = ['Licencia', 'Conteo', 'Porcentaje']

# 2. Filtros en sidebar
with st.sidebar:
    st.subheader("⚙️ Filtros")
    min_repos = st.slider(
        "Mínimo de repositorios:",
        min_value=1,
        max_value=int(license_stats['Conteo'].max()),
        value=5
    )
    show_unknown = st.checkbox("Mostrar licencias no especificadas", True)

# 3. Aplicar filtros
filtered_licenses = license_stats[license_stats['Conteo'] >= min_repos]
if not show_unknown:
    filtered_licenses = filtered_licenses[~filtered_licenses['Licencia'].str.contains('None', na=True)]

# 4. Gráfico principal (Barras horizontales)
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

# 5. Tabla compacta bajo el gráfico
with st.expander("📋 Ver datos tabulares", expanded=False):
    st.dataframe(
        filtered_licenses.style.format({'Porcentaje': '{:.2%}'}),
        height=300,
        use_container_width=True
    )

# 6. Gráfico secundario (Pie chart)
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

# LANGUAGE AND LICENSE ANALYSIS - STREAMLIT VERSION
st.header("🔧 Análisis Agrupado de Lenguajes y Licencias")

# 1. Calculate thresholds dynamically
col1, col2 = st.columns(2)
with col1:
    lang_threshold = st.slider("Umbral mínimo para lenguajes", 1, 50, 12)
with col2:
    license_threshold = st.slider("Umbral mínimo para licencias", 1, 100, 40)

# 2. Apply grouping logic
biggest_languages = language_count[language_count['Conteo'] >= lang_threshold]
biggest_licenses = license_stats[license_stats['Conteo'] >= license_threshold]

clean_df = repos_df.copy()
clean_df['language'] = clean_df['language'].apply(
    lambda x: 'Other' if x not in biggest_languages['Lenguaje'].values else x
)
clean_df['License'] = clean_df['License'].apply(
    lambda x: 'Other' if x not in biggest_licenses['Licencia'].values else x
)

# 3. Interactive visualization
st.subheader("Comparación de Forks y Pull Requests por Lenguaje")

metric_choice = st.multiselect(
    "Selecciona métricas a comparar:",
    options=['forks', 'pull_requests', 'stargazers_count', 'open_issues'],
    default=['forks', 'pull_requests']
)

if metric_choice:
    fig = px.bar(
        clean_df.sort_values('forks', ascending=False),
        x='language',
        y=metric_choice,
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={'value': 'Count', 'variable': 'Metric', 'language': 'Language'},
        hover_data=['License']
    )
    fig.update_layout(
        xaxis_title="Lenguaje de Programación",
        yaxis_title="Cantidad",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 4. Show aggregated data
    with st.expander("📊 Ver datos agregados"):
        agg_df = clean_df.groupby('language')[metric_choice].sum().sort_values(metric_choice[0], ascending=False)
        st.dataframe(
            agg_df.style.background_gradient(cmap='Blues'),
            use_container_width=True
        )
else:
    st.warning("Por favor selecciona al menos una métrica para visualizar")