import streamlit as st
import pandas as pd
import plots
import json

from pyecharts.charts import Map
from streamlit_echarts import st_echarts, st_pyecharts
import streamlit_echarts


def update(key, value):
    if key not in st.session_state:
        st.session_state[key] = value


st.set_page_config(page_title="U.S. Fatal Force Data Analysis", layout="centered")

st.markdown(
"""
# U.S. Fatal Force
In this dashboard, you will explore the data related to **fatal force** in the United States. The data was collected
from multiple sources. 

**2000–2016:**
> [**Kaggle:** rishidamarla/individuals-killed-by-the-police](https://www.kaggle.com/datasets/rishidamarla/individuals-killed-by-the-police)

**2016–2021:**
> [**Washington Post:** github.com/washingtonpost](https://github.com/washingtonpost/data-police-shootings)
"""
)

# adjust main block width
st.markdown('''
<style>
    section.main > div {max-width:70rem}
    [data-testid="stDataFrameResizable"] {
        border: 2px solid rgba(250, 250, 250, 0.1) !important;}
</style>
''', unsafe_allow_html=True)

# fix dataframe jitter
st.write('''<style>
[data-testid="stDataFrameResizable"] {
        border: 2px solid rgba(250, 250, 250, 0.1) !important;
}
</style>''', unsafe_allow_html=True)

# get the data
df = plots.getNormalData()

# dataframe metrics and dataframe display
with st.expander("***Show a summary of the dataset***", expanded=False):
    rows, buffer, cols = st.columns([1,1,1])
    rows.metric("**Total rows**", format(df.shape[0], ","))
    cols.metric('**Total columns**', df.shape[1])

    st.dataframe(df.sort_values(by='Year', ascending=False),
                 use_container_width=True,
                 hide_index=True,
                 column_config={'Year': st.column_config.NumberColumn("Year", format="%d")})

# define sidebar components
st.sidebar.header('Data Selection')
year = st.sidebar.selectbox('Choose a year to view',
                            ['All years'] + sorted(df['Year'].unique()))
st.sidebar.write("<br/>", unsafe_allow_html=True)
states = st.sidebar.multiselect('Choose a state',
                                ["All states"] + sorted(list(df['State'].unique())),
                                "All states")

# get data needed for the plots
race_grid, race_plot_df = plots.race_plot(df, year, states)
cities_grid, cities_output = plots.cities_plot(df, year, states)

# two column data visualization
col1, col2 = st.columns([1,1])

with col1:
    st.markdown("#### Race Plot Chart")
    st_pyecharts(race_grid, height='325px', width='100%', renderer='svg')

with col2:
    st.markdown("#### U.S. Fatal Force")
    plots.render_usa(df, year, states)\

col1, col2 = st.columns([2,.9])

with col1:
    st.markdown("#### Cities Plot Chart")
    st_pyecharts(cities_grid, height='500px', width='100%', renderer='svg')

with col2:
    st.markdown("#### Cities Data")
    st.write("<br/><br/>", unsafe_allow_html=True)
    st.dataframe(cities_output.sort_values('count', ascending=False), hide_index=True, use_container_width=True)
