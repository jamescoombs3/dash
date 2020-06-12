
import flask; import plotly.express as px
import dash; import dash_core_components as dcc; import dash_html_components as html
from dash.dependencies import Input, Output

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)
tips= px.data.tips(); fig = px.scatter(tips, x="total_bill", y="tip")
app.layout = html.Div([ dcc.RadioItems(id="gender1", options=[{'label': 'Female', 'value': 'Female'},
                                                              {'label': 'Male', 'value': 'Male'}], value='Female'),
                        dcc.Graph(id="fig1", figure=fig)])
@app.callback(Output('fig1', 'figure'),[Input('gender1', 'value')])
def updateGender(g): return px.scatter(tips.query("sex=='"+g+"'"), x="total_bill", y="tip")
if __name__ == '__main__':
    app.server.run(debug=True, use_reloader=False)

