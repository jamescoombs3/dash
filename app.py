import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.io as pio
import flask

server = flask.Flask(__name__)
# Initialize the app - style sheet is in ./assets/style.css so does not need to be specified eg:
# app = dash.Dash(__name__, external_stylesheets='./assets/style.css')
app = dash.Dash(__name__)

# Define the app
app.layout = html.Div()
app.config.suppress_callback_exceptions = True

# load the data
# workdir = 'C:/1drive/OneDrive - Three/_avado_Masters/2020/Data_Exp+Visualisation/Coursework2-20200617/'
# oxfix = pd.read_csv(workdir + 'oxfix.csv')
# To facilitate potentially getting this to run under heroku upload the CSV to a website
oxfix = pd.read_csv('https://trak.org.uk/wp-content/uploads/2020/07/oxfix.csv')

# Get population figures from UN. WARNING this is sensitive to the UN changing the location or format!!
# un_csv = 'https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/CSV_FILES/WPP2019_TotalPopulationBySex.csv'
# unpop = pd.read_csv(un_csv, usecols=[1, 4, 8])
unpop = pd.read_csv('https://trak.org.uk/wp-content/uploads/2020/07/UN2020pops.csv')

# oxfix.T.index; unpop.T.index   # Both dataframes use 'CountryCode' and 'CountryName'
# pandas.merge() will do an inner merge on common column names.
ox_sample = pd.merge(oxfix, unpop)

# Take our 'sample' of records to look at just 2 May (178 rows × 10 columns)
ox_sample = ox_sample[ox_sample['Date'].isin(['20200502'])]

# Create a new column mort_rate which is ConfirmedDeaths / population2020  (178 rows × 11 columns)
ox_sample = ox_sample.assign(mort_rate=ox_sample.ConfirmedDeaths/ox_sample.population2020)

# To manually check the highest mortality rates ...
# ox_sample['mort_rate'].sort_values().tail(15)

# Drop countries with populations less than a million
ox_sample = ox_sample[ox_sample['population2020'] > 1000]

# Not stricly necessary, but removing unwanted columns makes coding easier
ox_sample.drop(['Date', 'School closing', 'Stay at home requirements', 'ConfirmedCases',
                'ConfirmedDeaths', 'StringencyIndex', 'population2020'], axis=1, inplace=True)

pio.templates.default = 'plotly_dark'

# Unused! Might be useful to use a dictionary of attributes if using plotly graph objects (although using px here)
# layout = go.Layout({'title': 'What does this do?', 'showlegend': False})

# The values in Oxford database are all capitalised so can be used unchanged as titles for the dropdown
dd_options = [{'label': 'World', 'value': 'World'},
              {'label': 'Asia', 'value': 'Asia'},
              {'label': 'Africa', 'value': 'Africa'},
              {'label': 'Europe', 'value': 'Europe'},
              {'label': 'North America', 'value': 'North America'},
              {'label': 'South America', 'value': 'South America'}]

plot_data_options = [{'label': 'Confirmed COVID-19 Cases', 'value': 'ConfirmedCases'},
                {'label': 'Confirmed COVID-19 Deaths', 'value': 'ConfirmedDeaths'},
                {'label': 'Government Action/Interventions', 'value': 'StringencyIndex'},
                {'label': 'School and College Closures', 'value': 'School closing'},
                {'label': 'Stay at home measures ("Lockdown")', 'value': 'Stay at home requirements'},
                ]

# create dictionaries to enable a 'reverse' lookup of value to label for the radio options

plot_data_dict = {}
for i in range(0, plot_data_options.__len__()):
    plot_data_dict[plot_data_options[i]['value']] = plot_data_options[i]['label']

"""
rad2_dict = {}
for i in range(0, rad2_options.__len__()):
    rad2_dict[rad2_options[i]['value']] = rad2_options[i]['label']
"""

OxCGRT_web = 'https://www.bsg.ox.ac.uk/research/publications/variation-government-responses-covid-19'

# HTML layout
app.layout = html.Div(children=[
    html.Div(className='row', children=[
        html.Div(className='three columns div-user-controls', children=[
             html.H1('COVID-19 DASHBOARD'),
             html.Div(id='clustergram-control-tabs', children=[
                 dcc.Tabs([
                    dcc.Tab(label='About', children=[
                        html.H4('OxCGRT: Oxford University\’s'),
                        html.H4('Government Response Tracker'),
                        html.P('This demo takes data on COVID-19 collected by a team of over one '
                               'hundred contributors from around the world under the auspices of '
                               'Oxford University’s OxCGRT. '),
                        html.P('The responses taken by national '
                               'governments as well as the outcomes in terms of confirmed '
                               'infections and deaths are plotted on an animated geographical '
                               'context running from the beginning of March to the middle of May. '),
                        html.P('In the “Controls” tab you can change the scope to display figures for '
                               'the entire world or focus a single continent and choose which data to plot.'),
                    ]),
                    dcc.Tab(label='Controls', children=[
                        html.Br(),
                        html.P('Select from the dropdowns and click the play button'),
                        html.H1('Geographic Scope:'),
                        # html.P('Select either the whole world or individual continent from the dropdown list'),
                         html.Div(
                             className='div-for-dropdown',
                             children=[
                                 dcc.Dropdown(id='geo_scope', options=dd_options,
                                              multi=False, value='World',
                                              style={'backgroundColor': '#1E1E1E'},
                                              className='geo_scope',
                                              clearable=False,
                                              ),
                             ],
                             style={'color': '#1E1E1E'}),

                        html.H1('Data:'),

                        html.Div(
                            className='div-for-dropdown',
                            children=[
                                dcc.Dropdown(id='plot_data', options=plot_data_options,
                                             multi=False, value='ConfirmedCases',
                                             style={'backgroundColor': '#1E1E1E'},
                                             className='plot_data',
                                             clearable=False,
                                             ),
                            ],
                            style={'color': '#1E1E1E'}),
                        html.P(id='context_help'),
                        html.A('Oxford University COVID-19 Tracker (OxCGRT)',
                               href=OxCGRT_web),
                        html.P(id='thumb_title'),
                        dcc.Graph(id='thumb_graph'),
                     ]),
                 ]),
              ]),
        ]),   # End of the two/three columns div
        html.Div(className='nine columns div-for-charts bg-grey', style={'background-color': '#111111'}, children=[
            html.H1(id='graph_title', style={'text-align': 'center'}),
            # dcc.Graph(id='scope_id'),
            # dcc.Graph(id='test', config={'displayModeBar': False}, animate=True, figure=draw_graph('europe')),
            # html.H1(id='graph_update'),   # to debug the function before making it actually graph
            dcc.Graph(id='graph_update'),
            # html.H1('some text'),
        ])
    ])
])

# * * * * C A L L B A C K S * * * *
# Callback for updating the graph title
@app.callback(Output('graph_title', 'children'),
              [Input('geo_scope', 'value'),
               Input('plot_data', 'value')])
def update_title(continent, rad_1):
    title = 'Showing ' + plot_data_dict[rad_1] + ' for ' + continent.title()
    print('DEBUGut: update_title() title is:', title)
    return title


# Callback for updating the *thumbnail* graph title
# It should be possible to combine this with the above and create two outputs ... not sure I'm that brave yet!
@app.callback(Output('thumb_title', 'children'),
              [Input('plot_data', 'value')])
def update_thumb(rad_1):
    title = 'Thumbnail shows ' + plot_data_dict[rad_1] + \
            ' for the five countries with the highest deaths per captia over the period'
    print('DEBUGtt: update_title() title is:', title)
    return title

# Callback for updating the contextual help
@app.callback(Output('context_help', 'children'),
              [Input('plot_data', 'value')])
def context_help(plot_data):
    context_help = {
        'ConfirmedCases':
            'Displays national figures for number of confirmed infections. It should be borne in mind that '
            'different governments have different testing policies.',
        'ConfirmedDeaths':
            'Displays national figures for deaths from COVID-19. It should be borne in mind that different '
            'governments have different ways of counting official death statistics. ',
        'StringencyIndex':
            'The Oxford University COVID-19 tracking team combine a wide range of indicators, such '
            'as school closure, cancellation of large gatherings and closing public transport and combine '
            'all of these in a single index reflecting individual government responses to coronavirus which '
            'ranges from 0 to 100 (percent). For more details click on the link below.',
        'School closing':
            'This displays School, College and University closures on an ordinal scale from 0 to 3 where 0 '
            'indicates no closures, 1 indicates that closure is recommended but not mandated, 2 requires '
            'closure of some schools, eg high schools but not primary and 3 requires closure of all schools.',
        'Stay at home requirements':
            'This displays work closures on an ordinal scale from 0 to 3 where 0 indicates no closures, 1 indicates '
            'that closure is recommended but not mandated, 2 requires closure of some sectors or categories of '
            'worker and 3 requires closure of all but essential workplaces (e.g. grocery stores, doctors)'}
    print('DEBUGch: context_help() string returned is:', context_help[plot_data])
    return context_help[plot_data]

# Callback to update thumbnail graph
@app.callback(Output('thumb_graph', 'figure'),
              [Input('geo_scope', 'value'),
               Input('plot_data', 'value')])
def update_thumb_graph(continent, rad_1):
    print('\n\nENTERING update_thumb_graph()')
    print('=============================')
    print('DEBUGutg: geological scope is:', continent)
    print('DEBUGutg: choice of plot type is:', rad_1)
    print('DEBUGutg: ox_sam_local shape should be (158, 4) and is:', ox_sample.shape)
    print('DEBUGutg: oxfix_local shape should be (14418, 9) and is:', oxfix.shape)

    # If plotting a continent need to find
    # To plot a subset of oxfix based on the top5 first find countries within the select scope ...
    if continent != 'World':
        top5 = ox_sample[ox_sample['Continent_Name'] == continent]
    else:
        top5 = ox_sample
    # ... and of them the top five by mortality rate
    print('DEBUGutg: top5 shape is:', top5.shape)
    top5 = top5.sort_values('mort_rate').tail(5)['CountryCode']
    print('DEBUGutg: top5 includes the country code:', str(top5[:1]))

    df = pd.DataFrame()
    for c in top5:
        # oxfix[oxfix['CountryCode'] == c]
        df = df.append(oxfix[oxfix['CountryCode'] == c])
    print('DEBUGutg: df dataframe should have 81x5 rows and be (405, 9). It is:', df.shape)
    print('DEBUGutg: one of df cols should be "Date" and running dtypes returns:\n', df.dtypes)

    fig = px.line(df, x='Date', y=rad_1, color='CountryName')
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(width=400, height=200, margin=dict(l=0, r=0, b=0, t=0, pad=0))
    return fig


# Callback for updating the graph itself
@app.callback(Output('graph_update', 'figure'),
              [Input('geo_scope', 'value'),
               Input('plot_data', 'value')])
def graph_update(scope, data):
    # print('DEBUGgu: graph_update() scope =', scope)
    # print('DEBUGgu: graph_update() data =', data)
    global figx
    figx = None
    # the scope property of layout.geo is one of
    # ['world', 'usa', 'europe', 'asia', 'africa', 'north america', 'south america']
    # this *almost* exactly matches the values used by OxCGRT but in lower case
    scope = scope.lower()
    ox_sub = oxfix
    if scope == 'world':
        projection = 'natural earth'
        size_max = 20
    else:
        projection = 'equirectangular'
        size_max = 80

    # five things to plot, if confirmed cases/deaths use bubble else choropleth
    if data == 'ConfirmedCases' or data == 'ConfirmedDeaths':
        # print('DEBUGgu: scatter_geo (bubble) plot needed')
        figx = px.scatter_geo(ox_sub,
                              locations='CountryCode',
                              projection=projection,
                              color='Continent_Name',
                              scope=scope,
                              hover_name='CountryName',
                              size=data,
                              animation_frame='Date',
                              size_max=size_max,
                              )
        figx.update(layout_showlegend=False)
    else:
        # print('DEBUGgu: choropleth plot needed')
        figx = px.choropleth(ox_sub,
                             locations='CountryCode',
                             projection=projection,
                             color=data,
                             scope=scope,
                             hover_name='CountryName',  # column to add to hover information
                             animation_frame='Date',
                             color_continuous_scale='YlOrRd_r',
                             )
    # common updates to both graph types
    figx.update_layout(transition_duration=300)  # ... appears to have no effect!
    pal = {'background': '#111111', 'text': '#7FDBFF'}
    figx.update_layout(plot_bgcolor=pal['background'], paper_bgcolor=pal['background'], font_color=pal['text'])
    figx.update_geos(showcoastlines=True, coastlinecolor="DarkBlue",
                     showland=True, landcolor="DarkGreen",
                     showocean=True, oceancolor="LightBlue")
    figx.update_layout(autosize=True,
                       # paper_bgcolor="LightSteelBlue",  # for debugging layout, uncomment this.
                       width=1400, height=800,
                       margin=dict(l=0, r=0, b=0, t=0, pad=4))
    return figx

# Run with use_reloader=False 
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)

