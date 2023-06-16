import pandas as pd
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output


app = dash.Dash(__name__)


# clearing data
df = pd.read_csv('BPD_arrests.csv')
df.dropna(inplace=True)
df.dropna(subset=['Arrest', 'Age', 'Sex', 'Race', 'ArrestDate',
          'ArrestTime', 'ArrestLocation'], inplace=True)
df.reset_index(drop=True, inplace=True)
df['Year'] = pd.to_datetime(df['ArrestDate']).dt.year
df['Neighborhood'] = df['Neighborhood'].str.upper()
df['ChargeDescription'] = df['ChargeDescription'].str.upper()
df = df[df['Age'] != 0]
df['ArrestTime'] = pd.to_datetime(df['ArrestTime'], format='%H:%M')
df.sort_values('ArrestTime', inplace=True)
df['ArrestDate'] = pd.to_datetime(df['ArrestDate'], format='%m/%d/%Y')
df.reset_index(drop=True, inplace=True)


# values for slider
marks_values = {2013: '2013', 2014: '2014', 2015: '2015', 2016: '2016'}

# lists of columns for regression and classification graphs
regr_column_list = ['ArrestDate', 'ArrestTime']
class_column_list = ['Age', 'Sex', 'Race', 'ArrestDate', 'ArrestTime', 'Year']

# list of charges
charge_descriptions = [
    'ROBB',
    'PROSTITUTION',
    'NARC',
    'TRESPASS',
    'THEFT',
    'ASSAULT',
    'SEX'
]

dataframes = {}
# iterating through list of charges to add them to dropdown
for charge in charge_descriptions:
    stripped_charge = charge.upper().strip().replace(':', '').replace('-', '')
    df_charge = df[df['ChargeDescription'].str.upper().str.strip().str.contains(stripped_charge.upper()) |
                   df['IncidentOffense'].str.upper().str.strip().str.contains(stripped_charge.upper())]
    dataframes[charge] = df_charge

# grouping variables
crime_locations = df.groupby(
    ['Neighborhood']).size().reset_index(name='CrimeCount')
crime_locations = crime_locations.sort_values(by='CrimeCount', ascending=False)

most_dangerous_neighborhood = crime_locations['Neighborhood'].iloc[0]
filtered_df = df[df['Neighborhood'] == most_dangerous_neighborhood]
arrests_by_year = filtered_df.groupby(
    'Year').size().reset_index(name='ArrestCount')

robbery_crimes = df[df['ChargeDescription'].str.contains(
    'robbery', case=False)]

criminals_by_age = df.groupby(['Age']).size().reset_index(name='CriminalCount')
criminals_by_age = criminals_by_age.sort_values(
    by='CriminalCount', ascending=False)

criminals_by_sex = df.groupby(['Sex']).size().reset_index(name='CriminalCount')
criminals_by_sex = criminals_by_sex.sort_values(
    by='CriminalCount', ascending=False)

age_and_sex = df.groupby(['Sex', 'Age']).size(
).reset_index(name='CriminalCount')
age_and_sex = age_and_sex.sort_values(by='CriminalCount', ascending=False)

criminals_by_race = df.groupby(
    ['Race']).size().reset_index(name='CriminalCount')
criminals_by_race = criminals_by_race.sort_values(
    by='CriminalCount', ascending=False)

race_and_year = df.groupby(['Race', 'Age', 'Year']
                           ).size().reset_index(name='CrimeCount')
race_and_year = race_and_year.sort_values(by='CrimeCount', ascending=False)


# data for drug traf graph
charge_description = 'DRUG'
drug_charge = df[df['ChargeDescription'].str.upper(
).str.strip().str.contains(charge_description)]

robbery_crimes = df[df['IncidentOffense'].str.contains(
    'narcotics', case=False)]

# data for burglary graph
burglary = 'BURG'
burglary_charge = df[df['ChargeDescription'].str.upper().str.strip().str.contains(charge_description) |
                     df['IncidentOffense'].str.upper().str.strip().str.contains(charge_description)]
burglary_charge = burglary_charge.groupby(
    'Year').size().reset_index(name='CrimeCount')

# figs
fig1 = px.line(
    arrests_by_year,
    x="Year",
    y="ArrestCount",
    width=200,
    title=f"Changes in the most dangerous area over the years: {most_dangerous_neighborhood}")

fig2 = px.scatter(age_and_sex, x="Age", y="CriminalCount", color="Sex",
                  title=f"Number of criminals depending on age and sex")

fig4 = px.bar(criminals_by_sex, y='CriminalCount', x='Sex', color='Sex')

fig5 = px.scatter(race_and_year,
                  x="Age",
                  y="CrimeCount",
                  color="Race",
                  title=f"Number of criminals depending on age and race")

burg_figure = px.bar(
    burglary_charge,
    x="Year",
    y="CrimeCount",
    color="Year",
    title=f"Number of apartment burglaries over the years",
)

# layout
app.layout = html.Div([
    html.Div([
        html.H1('Baltimore Police Department reports 2013-2016',
                style={'textAlign': 'center'})
    ]),
    html.Div([
        dcc.Graph(
            id='crime-graph',
        ),
        html.P('Change neighborhood count', style={'textAlign': 'center'}),
        dcc.Slider(
            min=5,
            max=100,
            id='slider',
            value=15,
            step=5,
        ),
    ]),
    html.Div([
        dcc.Graph(
            id='changes-line',
            figure=fig1
        ),
    ]),
    html.Div([
        html.H1('Multiple choices'),
        dcc.Dropdown(
            id='dropdown1',
            options=[
                {'label': 'Age', 'value': 'Age'},
                {'label': 'Sex', 'value': 'Sex'},
                {'label': 'Race', 'value': 'Race'}
            ],
            value='Age',
            style={'width': '200px', 'margin-right': '20px'}
        ),
        dcc.Dropdown(
            id='dropdown2',
            options=[
                {'label': 'Age', 'value': 'Age'},
                {'label': 'Sex', 'value': 'Sex'},
                {'label': 'Race', 'value': 'Race'}
            ],
            value='Sex',
            style={'width': '200px'}
        ),
    ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-right': '40px'}),
    dcc.Graph(
        id='combined-graph',
        figure={}
    ),
    html.P('Change year', style={'textAlign': 'center'}),
    dcc.RangeSlider(
        min=2013,
        max=2016,
        id='the-year',
        value=[2013, 2016],
        marks=marks_values,
        step=None,
    ),
    html.Div([
        html.H1("Offense by location"),
        html.Label("Select a location:"),
        dcc.Dropdown(
            id='location-dropdown',
            options=[{'label': loc, 'value': loc}
                     for loc in df['Neighborhood'].unique()],
            value=df['Neighborhood'].unique()[0]
        ),
        html.H4(id='unknown-offense-percent'),
        dcc.Graph(id='crime-bar-chart'),
        html.P('Change offense count', style={'textAlign': 'center'}),
        dcc.Slider(
            min=2,
            max=50,
            id='slider2',
            value=15,
            step=5,
        ),
    ]),
    html.Div([
        html.H1("Chose crime"),
        dcc.Dropdown(
            id='charge-dropdown',
            options=[{'label': charge, 'value': charge}
                     for charge in charge_descriptions],
            value=charge_descriptions[0]
        ),
        dcc.Graph(
            id='neighborhood-bar'
        )
    ]),
    html.Div([
        dcc.Graph(
            id='drug-traf-trend'
        ),
        dcc.RangeSlider(
            id='year-slider',
            min=2013,
            max=2016,
            value=[2013, 2016],
            marks=marks_values,
            step=None
        ),
    ]),
    html.Div([
        dcc.Graph(
            id='burglary-trend',
            figure=burg_figure
        )
    ]),
    html.Div([
        html.H1("Regr/Class"),

        html.Label("Select Model:"),
        dcc.Dropdown(
            id='model-dropdown',
            options=[
                {'label': 'Regression', 'value': 'regression'},
                {'label': 'Classification', 'value': 'classification'}
            ],
            value='regression'
        ),

        html.Label("Select Variable:"),
        dcc.Dropdown(id='variable-dropdown'),

        html.Div(id='graph-container')
    ]),
])


# regression/classification callback and function
@app.callback(
    Output('variable-dropdown', 'options'),
    [Input('model-dropdown', 'value')]
)
def update_variable_dropdown(model):
    if model == 'regression':
        variables = df[regr_column_list]
    else:
        variables = df[class_column_list]

    options = [{'label': variable, 'value': variable}
               for variable in variables]
    return options


# regression/classification callback and function
@app.callback(
    Output('graph-container', 'children'),
    [Input('model-dropdown', 'value'),
     Input('variable-dropdown', 'value')]
)
def generate_graph(model, variable):
    if model == 'regression':
        fig = px.scatter(df, x=variable, y='Age', color='Sex')
    else:
        fig = px.histogram(df, x=variable, color='Race')

    graph = dcc.Graph(figure=fig)
    return graph


# drug traf trend over the years
@app.callback(
    Output('drug-traf-trend', 'figure'),
    Input('year-slider', 'value')
)
def update_drug_traf_trend(year_range):
    df_filtered = df_charge[(df_charge['Year'] >= year_range[0]) & (
        df_charge['Year'] <= year_range[1])]
    year_counts = df_filtered.groupby(
        'Year').size().reset_index(name='CrimeCount')

    fig = px.line(year_counts, x='Year', y='CrimeCount',
                  title=f'Trend of {charge_description} Crimes from {year_range[0]} to {year_range[1]}')

    fig.update_layout(xaxis_title='Year', yaxis_title='Crime Count')

    return fig


# locations with most crimes
@app.callback(
    Output('neighborhood-bar', 'figure'),
    Input('charge-dropdown', 'value')
)
def update_neighborhood_bar(charge):
    df_charge = dataframes[charge]
    neighborhood_counts = df_charge['Neighborhood'].value_counts(
    ).reset_index()
    neighborhood_counts.columns = ['Neighborhood', 'CrimeCount']
    neighborhood_counts = neighborhood_counts.sort_values(
        by='CrimeCount', ascending=False)
    neighborhood_counts = neighborhood_counts.head(40)

    fig = px.bar(neighborhood_counts, x='Neighborhood', y='CrimeCount', text='CrimeCount',
                 title=f'Neighborhoods with the Most {charge} Crimes')
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(xaxis={'categoryorder': 'total descending'})

    return fig


# offense by chosen location
@app.callback(
    [Output('crime-bar-chart', 'figure'),
     Output('unknown-offense-percent', 'children')],
    [Input('location-dropdown', 'value'),
     Input('slider2', 'value')]
)
def update_graph(selected_location, value):
    filtered_df = df[df['Neighborhood'] == selected_location]
    crimes_count = filtered_df['IncidentOffense'].value_counts().reset_index()
    crimes_count.columns = ['Crime', 'Count']
    crimes_count = crimes_count[crimes_count['Crime'] != 'Unknown Offense']
    filtered_locations = crimes_count.iloc[:value]

    fig = px.bar(filtered_locations, x='Crime', y='Count', text_auto='.2s')

    percent = (filtered_df['IncidentOffense'].value_counts(
    ) / filtered_df['IncidentOffense'].count()) * 100
    unknown_offense_percent = f"Unknown offense count in {selected_location}: {filtered_df['IncidentOffense'].value_counts()['Unknown Offense']} (~{round(percent['Unknown Offense'])}%)"

    return fig, unknown_offense_percent,


# graph with multiple choices (depending on two values)
@app.callback(
    Output('combined-graph', 'figure'),
    [Input('dropdown1', 'value'),
     Input('dropdown2', 'value'),
     Input('the-year', 'value')]
)
def update_combined_graph(dropdown1, dropdown2, selected_years):
    filtered_df = df[df['Year'].between(selected_years[0], selected_years[1])]

    if dropdown1 == dropdown2:
        fig = px.bar(filtered_df.groupby([dropdown1]).size().reset_index(name='CriminalCount'),
                     x=dropdown1,
                     y='CriminalCount',
                     color=dropdown1,
                     text_auto='.2s',
                     title=f'Number of criminals depending on {dropdown1}')
    elif dropdown1 != dropdown2:
        if dropdown1 == 'Sex' and dropdown2 == 'Race':
            fig = px.bar(filtered_df.groupby([dropdown1, dropdown2]).size().reset_index(name='CriminalCount'),
                         x=dropdown1,
                         y='CriminalCount',
                         color=dropdown2,
                         text_auto='.2s',
                         title=f'Number of criminals depending on {dropdown1} and {dropdown2}',)
            fig.update_layout(showlegend=True)
        elif dropdown1 == 'Race' and dropdown2 == 'Sex':
            fig = px.bar(filtered_df.groupby([dropdown1, dropdown2]).size().reset_index(name='CriminalCount'),
                         x=dropdown2,
                         y='CriminalCount',
                         color=dropdown1,
                         text_auto='.2s',
                         title=f'Number of criminals depending on {dropdown2} and {dropdown1}',)
            fig.update_layout(showlegend=True)
        elif dropdown1 == 'Sex' and dropdown2 == 'Age':
            fig = px.bar(filtered_df.groupby([dropdown1, dropdown2]).size().reset_index(name='CriminalCount'),
                         x=dropdown2,
                         y='CriminalCount',
                         color=dropdown1,
                         text_auto='.2s',
                         title=f'Number of criminals depending on {dropdown1} and {dropdown2}',)
            fig.update_layout(showlegend=True)
        elif dropdown1 == 'Race' and dropdown2 == 'Age':
            fig = px.bar(filtered_df.groupby([dropdown1, dropdown2]).size().reset_index(name='CriminalCount'),
                         x=dropdown2,
                         y='CriminalCount',
                         color=dropdown1,
                         text_auto='.2s',
                         title=f'Number of criminals depending on {dropdown2} and {dropdown1}',)
            fig.update_layout(showlegend=True)
        else:
            fig = px.scatter(filtered_df.groupby([dropdown1, dropdown2]).size().reset_index(name='CriminalCount'),
                             x=dropdown1,
                             y='CriminalCount',
                             color=dropdown2,
                             title=f'Number of criminals depending on {dropdown1} and {dropdown2}')
    return fig


# graph that shows most dangerous locations
@app.callback(
    Output('crime-graph', 'figure'),
    Input('slider', 'value'))
def crime_graph(value):
    filtered_locations = crime_locations.iloc[:value]
    fig = px.bar(filtered_locations, x='Neighborhood', y='CrimeCount', text_auto='.2s',
                 title="Crime Locations")
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
