import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import streamlit as st
import json

import pyecharts.options as opts
from streamlit_echarts import Map, JsCode, st_echarts
from pyecharts.charts import Bar, Grid


def abbrev_to_state(df):
    abbrev_to_state = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming',
        'PR': 'Puerto Rico',
        'VI': 'Virigin Islands'
    }

    df['State'] = df['State'].str.strip().replace(abbrev_to_state)
    return df

def getNormalData():
    df = pd.read_csv('https://raw.githubusercontent.com/s-lasch/CIS-280/main/police_fatalities.csv').drop(columns=['UID'])
    df = abbrev_to_state(df)
    return df

def validate_state(df, year, state):
    if state == ['All states'] and year == 'All years':
        dff = df
        return dff

    elif state == ['All states'] and year != 'All years':
        dff = df[ df['Year'] == year ].reset_index(drop=True)
        return dff

    elif state != ['All states'] and year == 'All years':
        dff = df[ df['State'].isin(state) ].reset_index(drop=True)
        return dff

    elif state != ['All states'] and year != 'All years':
        dff = df[ (df['State'].isin(state)) & (df['Year'] == year) ].reset_index(drop=True)
        return dff

    elif state is None:
        st.error('Please select a valid state.')

def race_plot(df, year, state):
    df = validate_state(df, year, state)

    # must be in ascending order to render the bar plot
    race = df.value_counts(['Race']).to_frame().reset_index().sort_values(by='count')

    bar = (
        Bar()
        .add_xaxis(list(race['Race']))
        .add_yaxis("Deaths", list(race['count']))
        .reversal_axis()
        .set_series_opts(label_opts=opts.LabelOpts(position="right"),
                         itemstyle_opts=opts.ItemStyleOpts(border_radius=5))
        .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
    )

    grid = Grid().add(bar, grid_opts=opts.GridOpts(pos_left='22%'))
    return grid, race

def cities_plot(df, year, state):
    df = validate_state(df, year, state)

    # must be in ascending order to render the bar chart
    cities = df.value_counts(['City', 'State']).to_frame().reset_index().head(10).sort_values(by='count')

    bar = (
        Bar()
        .add_xaxis(list(cities['City']))
        .add_yaxis("Deaths", list(cities['count']))
        .reversal_axis()
        .set_series_opts(label_opts=opts.LabelOpts(position="right"),
                         itemstyle_opts=opts.ItemStyleOpts(border_radius=5))
        .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
    )

    grid = Grid().add(bar, grid_opts=opts.GridOpts(pos_left='15%', pos_right='15%'))
    return grid, cities

def map_data(df, year, state):
    dff = validate_state(df, year, state)

    states = (dff.value_counts(['State'])
              .to_frame()
              .reset_index()
              .rename(columns={'State': 'name', 'count': 'value'})
              # .to_dict(orient='records')
              )

    return states

# TODO: See if this map can be implemented using the pyecharts API.
def render_usa(df, year, state):
    formatter = JsCode(
        "function (params) {"
        + "var value = (params.value + '').split('.');"
        + "value = value[0].replace(/(\d{1,3})(?=(?:\d{3})+(?!\d))/g, '$1,');"
        + "return params.seriesName + '<br/>' + params.name + ': ' + value;}"
    ).js_code

    with open("data/usa.json", "r") as f:
        map = Map(
            "USA",
            json.loads(f.read()),
            {
                # "Alaska": {"left": -131, "top": 25, "width": 15},
                "Hawaii": {"left": -110, "top": 25, "width": 5},
                # "Puerto Rico": {"left": -76, "top": 26, "width": 2},
            },
        )
    options = {
        "title": {
            # "text": "USA Population Estimates (2012)",
            "subtext": "Color scale based on average national deaths.",
            "left": "right",
        },
        "tooltip": {
            "trigger": "item",
            "showDelay": 0,
            "transitionDuration": 0.2,
            "formatter": formatter,
        },
        "visualMap": {
            "left": "right",
            "min": 0,
            "max": int(map_data(df,year,state)['value'].mean()),
            "inRange": {
                "color": [
                    "#313695",
                    "#4575b4",
                    "#74add1",
                    "#abd9e9",
                    "#e0f3f8",
                    "#ffffbf",
                    "#fee090",
                    "#fdae61",
                    "#f46d43",
                    "#d73027",
                    "#a50026",
                ]
            },
            "text": ["High", "Low"],
            "calculable": True,
        },
        "toolbox": {
            "show": True,
            "left": "left",
            "top": "top",
            "feature": {
                "dataView": {"readOnly": False},
                "restore": {},
                "saveAsImage": {},
            },
        },
        "series": [
            {
                "name": "<b>Deaths</b>",
                "type": "map",
                "roam": True,
                "map": "USA",
                "emphasis": {"label": {"show": True}},
                "textFixed": {"Alaska": [20, -20]},
                "data": map_data(df,year,state).to_dict(orient="records"),
            }
        ],
    }
    return st_echarts(options=options, map=map, renderer='svg')

def gender_pie(df, year, state):
    df = validate_state(df, year, state)

    # filter by gender and get the value_counts
    gender_counts = (df[(df['Gender'] == 'Male') | (df['Gender'] == 'Female')]['Gender']
                     .value_counts()
                     .to_frame()
                     .reset_index()
                     .rename(columns={'Gender': 'Count', 'count': 'Gender'})
                     )

    # create the pie chart
    fig = go.Figure(data=[go.Pie(labels=gender_counts['Gender'],
                                 values=gender_counts['Count'],
                                 customdata=[gender_counts['Gender'], gender_counts['Count']],
                                 hovertemplate='<br>'.join([
                                     '<extra></extra>',
                                     '<b>%{label}</b>',
                                     'Shootings: %{value}',
                                 ]),
                                 # hoverinfo='skip'
                                 )])

    # set the colors for male and female
    fig.update_traces(marker={'colors': px.colors.qualitative.D3})

    # update the title font size
    fig.update_layout(
        title=f'<b>Fatal Force Gender Disparity {year}</b><br><sub>Percentage of victims by their gender</sub></br>',
        title_font=dict(size=17),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_x=0.5)

    return fig

def gender_kde(df, gender, method='Mean'):
    # assign specific color depending on the gender
    if gender == 'Male':
        color = px.colors.qualitative.D3[0]
    else:
        color = px.colors.qualitative.D3[1]

    overall_color = '#D3D3D3'

    # create the distplot
    fig = ff.create_distplot([df[df['Gender'] == gender]['Age'], df['Age']],
                             group_labels=[gender, 'All Victims'],
                             show_rug=False,
                             show_hist=False,
                             colors=[color, overall_color],
                             histnorm='probability',
                             bin_size=6
                             )

    # update the title font size and the x and y axis labels
    fig.update_layout(title={
        'text': f'<b>Distribution of {gender} Victims</b><br><sub>Vertical lines represent the {method.lower()} of their ages</sub></br>',
        'font': {'size': 17}},
                      xaxis={'title': 'Age'},
                      yaxis={'title': 'Percentages'},
                      hovermode='x unified',
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      title_x=0.5
                      )

    # change the method for the vertical dashed line
    if method == 'Mean':
        # add a horizontal line that represents the overall median
        fig.add_vline(x=df['Age'].mean(),
                      line_dash='dash',
                      line=dict(color=overall_color))

        # add another horizontal line that represents the gender's median
        fig.add_vline(x=df[df['Gender'] == gender]['Age'].mean(),
                      line_dash='dash',
                      line=dict(color=color))

    elif method == 'Median':
        # add a horizontal line that represents the overall median
        fig.add_vline(x=df['Age'].median(),
                      line_dash='dash',
                      line=dict(color=overall_color))

        # add another horizontal line that represents the gender's median
        fig.add_vline(x=df[df['Gender'] == gender]['Age'].median(),
                      line_dash='dash',
                      line=dict(color=color))

    elif method == 'Mode':
        # add a horizontal line that represents the overall median
        fig.add_vline(x=df['Age'].mode()[0],
                      line_dash='dash',
                      line=dict(color=overall_color))

        # add another horizontal line that represents the gender's median
        fig.add_vline(x=df[df['Gender'] == gender]['Age'].mode()[0],
                      line_dash='dash',
                      line=dict(color=color))

    return fig
