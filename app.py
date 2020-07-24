import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.io as pio
import flask

# load the data
oxfix = pd.read_csv('https://trak.org.uk/wp-content/uploads/2020/07/oxfix.csv')

# some debate as to whether to specify a stylesheet or just have in the directory 
# ./assets/style.css

# Initialize the app
# app = dash.Dash(__name__, external_stylesheets='./assets/style.css')
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)
# app = dash.Dash(__name__)

# Define the app
app.layout = html.Div()

app.config.suppress_callback_exceptions = True

pio.templates.default = 'plotly_dark'

# Unused! Might be useful to use a dictionary of attributes if using plotly graph objects (although using px here)
# layout = go.Layout({'title': 'What does this do?', 'showlegend': False})

dd_options = [{'label': 'World', 'value': 'world'},
              {'label': 'Asia', 'value': 'asia'},
              {'label': 'Africa', 'value': 'africa'},
              {'label': 'Europe', 'value': 'europe'},
              {'label': 'North America', 'value': 'north america'},
              {'label': 'South America', 'value': 'south america'}]

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

OxCGRT_web = 'https://www.bsg.ox.ac.uk/research/publications/variation-government-responses-covid-19'

"""
rad2_dict = {}
for i in range(0, rad2_options.__len__()):
    rad2_dict[rad2_options[i]['value']] = rad2_options[i]['label']
"""

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
                        html.P('Select the geographic scope and the data to be plotted then click the play button'),
                        html.H1('Geographic Scope:'),
                        # html.P('Select either the whole world or individual continent from the dropdown list'),
                         html.Div(
                             className='div-for-dropdown',
                             children=[
                                 dcc.Dropdown(id='geo_scope', options=dd_options,
                                              multi=False, value='world',
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
                                             className='eek',
                                             clearable=False,
                                             ),
                            ],
                            style={'color': '#1E1E1E'}),
                        html.P(id='context_help'),
                        html.A('Oxford University COVID-19 Tracker (OxCGRT)',
                               href=OxCGRT_web)

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

# Callback for updating the graph title
@app.callback(Output('graph_title', 'children'),
              [Input('geo_scope', 'value'),
               Input('plot_data', 'value')])
def update_title(continent, rad_1):
    title = 'Showing ' + plot_data_dict[rad_1] + ' for ' + continent.title()
    print('DEBUG: update_title() title is:', title)
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
    # return 'this is a string'


# Callback for updating the graph itself
@app.callback(Output('graph_update', 'figure'),
              [Input('geo_scope', 'value'),
               Input('plot_data', 'value')])
def graph_update(scope, data):
    print('DEBUGgu: graph_update() scope =', scope)
    print('DEBUGgu: graph_update() data =', data)
    global figx
    figx = None

    ox_sub = oxfix
    if scope == 'world':
        projection = 'natural earth'
        size_max = 20
    else:
        projection = 'equirectangular'
        size_max = 80

    # five things to plot, if confirmed cases/deaths use bubble else choropleth
    if data == 'ConfirmedCases' or data == 'ConfirmedDeaths':
        print('DEBUGgu: scatter_geo (bubble) plot needed')
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
        print('DEBUGgu: choropleth plot needed')
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

# Run on port 8055 (becuase I have a few versions on the go ..)
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)

