import pandas as pd
import panel as pn
import plotly.express as px
from plotly.subplots import make_subplots
from bokeh.plotting import figure
import time

def getFrame(df, agg_func):
    if agg_func =='mean':
        frame = df.groupby(['Month_Year', 'Vehicle Type', 'Zone'], as_index=False)['value'].mean()
    elif agg_func=='sum':
        frame = df.groupby(['Month_Year', 'Vehicle Type', 'Zone'], as_index=False)['value'].sum()

    frame.sort_values(by='Month_Year', inplace=True)
    frame['Month_Year'] = frame['Month_Year'].dt.strftime('%B-%Y')
    return frame

pn.extension(template='bootstrap')
pd.options.display.max_rows=200
start = time.time()
print('Imports done in {}'.format(time.time()-start))


df = pd.read_parquet(r'results/SensorData.parquet')
df.reset_index(inplace=True)
# df['Month'] = df['Date_Time'].dt.month
# df['Year'] = df['Date_Time'].dt.year
print('File read and Month Year defined in {}'.format(time.time()-start))
a = time.time()
df['Month_Year'] = df['Date_Time'].dt.to_period('M')
print('"Month_Year" created in {}'.format(time.time()-a))

north = ['S20', 'S13', 'S19', 'S21', 'S18']
city = ['S10', 'S2', 'S41', 'S1', 'S4', 'S7', 'S15']
south = ['S12', 'S6', 'S14', 'S40', 'S3', 'S16']
df.loc[df['SensorID'].isin(north), 'Zone'] = 'North'
df.loc[df['SensorID'].isin(city), 'Zone'] = 'City'
df.loc[df['SensorID'].isin(south), 'Zone'] = 'South'

d1 = {'Car':'Small Vehicles', 'Pedestrian':'Pedestrians and Cyclists', 'Cyclist':'Pedestrians and Cyclists', 'Motorbike':'Small Vehicles', 'Bus':'Large Vehicles', 'OGV1':'Large Vehicles', 'OGV2':'Large Vehicles', 'LGV':'Large Vehicles'}
df['Vehicle Type'] = df['variable'].map(d1)
b = time.time()
print('Finished reading and creating zones in {}'.format(b-a))


# select = pn.widgets.Select(name='Select zone', options=df['Zone'].unique().tolist())
mapDf = df[['SensorID', 'Lat', 'Long', 'Street location', 'Zone']].copy()
mapDf = mapDf.drop_duplicates()
# mapDf = mapDf[mapDf['Zone'].isin([select.value])]

p1 = px.scatter_mapbox(mapDf, lat='Lat', lon='Long', mapbox_style="open-street-map", zoom=10, color='Zone', hover_name='Street location')
p1.update_traces(marker={'size': 12})
p1.update_layout(title='Sensor locations', hovermode='closest', width=1000)
c = time.time()
print('P1 created in {}'.format(c-b))


northTraffic = df[df['Zone'] == 'North'][['SensorID', 'Month_Year', 'Vehicle Type', 'value', 'Zone']]
northTrafficMean = getFrame(northTraffic, 'mean')
northTrafficSum = getFrame(northTraffic, 'sum')

cityTraffic = df[df['Zone'] == 'City'][['SensorID', 'Month_Year', 'Vehicle Type', 'value', 'Zone']]
cityTrafficMean = getFrame(cityTraffic, 'mean')
cityTrafficSum = getFrame(cityTraffic, 'sum')

southTraffic = df[df['Zone'] == 'South'][['SensorID', 'Month_Year', 'Vehicle Type', 'value', 'Zone']]
southTrafficMean = getFrame(southTraffic, 'mean')
southTrafficSum = getFrame(southTraffic, 'sum')

totalTrafficMean = pd.concat([northTrafficMean, cityTrafficMean, southTrafficMean], ignore_index=True)
totalTrafficSum = pd.concat([northTrafficSum, cityTrafficSum, southTrafficSum], ignore_index=True)


c1 = time.time()
print('Zonal traffic frames created in {}'.format(c1-c))
#
#
# # fig4 = px.bar(totalTraffic, x="Month_Year", y="value", color="Vehicle Type", barmode="group", facet_col="Zone", width=1000)
fig4 = px.area(totalTrafficMean, x="Month_Year", y="value", color="Vehicle Type", facet_col="Zone", width=1000, title='Average traffic per month')
fig5 = px.area(totalTrafficSum, x="Month_Year", y="value", color="Vehicle Type", facet_col="Zone", width=1000, title='Total traffic per month')

#
d = time.time()
print('Traffic DF in {}'.format(d-c1))

p2 = figure(width=300, height=300, name='Line')
p2.line([0, 1, 2, 3, 4, 5, 6], [0, 1, 2, 3, 2, 1, 0])

# trafficLines = pn.Row(northLine, cityLine, southLine)
gspec = pn.GridSpec(sizing_mode='stretch_both')
gspec[0:4, 0:5] = p1
# gspec[0:2, 2:3] = fig1
# gspec[2:4, 0:2] = fig2
# gspec[2:4, 2:3] = fig3
gspec[5:9, 0:5] = fig4
gspec[10:14, 0:5] = fig5

tab1 = gspec

tab2 = p2
tabs = pn.Tabs(tab1, tab2)
r = pn.Row(tabs).servable()

# points = hv.Points(mapDf, ["easting", "northing"]).opts(color="Zone")
# tiles = CartoDark()
# overlay = tiles * points
# print('Finished creating map dataframe')

# app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
# # app = Dash(__name__)
# app.layout = dbc.Container(
#     [
#         dcc.Store(id="store"),
#         html.H1("Traffic trends recorded in Cambridge 2019-2021"),
#         html.Hr(),
#         dbc.Button(
#             "Show locations",
#             color="primary",
#             id="button",
#             className="mb-3",
#         ),
#         dbc.Tabs(
#             [
#                 dbc.Tab(label="Location and Summary", tab_id="maps"),
#                 dbc.Tab(label="Traffic trends IN/OUT", tab_id="traffic"),
#                 dbc.Tab(label="Vehicular size stats", tab_id="size")
#             ],
#             id="tabs",
#             active_tab="maps",
#         ),
#         html.Div(id="tab-content", className="p-4"),
#     ]
# )


# @app.callback(
#     Output("tab-content", "children"),
#     [Input("tabs", "active_tab"), Input("store", "data")],
# )
# def render_tab_content(active_tab, data):
#     """
#     This callback takes the 'active_tab' property as input, as well as the
#     stored graphs, and renders the tab content depending on what the value of
#     'active_tab' is.
#     """
#     if active_tab and data is not None:
#         if active_tab == "maps":
#             # maps = px.scatter_mapbox(mapDf, lat="Lat", lon="Long", color='Zone', size_max=15, zoom=10, hover_name='Street location', hover_data=['SensorID'])
#             # maps.update_layout(mapbox_style="open-street-map")
#             # maps.update_traces(marker={'size': 12})

#             print('Finished drawing map')

#             frame = df[['Month_Year', 'value', 'variable', 'Zone', 'SensorID']].copy()
#             northDf = createGroup(frame, 'North')
#             cityDf = createGroup(frame, 'City')
#             southDf = createGroup(frame, 'South')

#             print('Groups ready...')

#             graph_northDf = px.line(northDf, x="Month_Year", y="value", color="variable", hover_name="variable", line_shape="spline", render_mode="svg")
#             graph_cityDf = px.line(cityDf, x="Month_Year", y="value", color="variable", hover_name="variable", line_shape="spline", render_mode="svg")
#             graph_southDf = px.line(southDf, x="Month_Year", y="value", color="variable", hover_name="variable", line_shape="spline", render_mode="svg")

#             components = to_dash(app, [overlay])
#             return dbc.Row(components.children)
#             # return dbc.Row(
#             #     [
#             #         dbc.Col(dcc.Graph(figure=maps), width=6),
#             #         dbc.Col([dbc.Row(dcc.Graph(figure=graph_northDf)),dbc.Row(dcc.Graph(figure=graph_cityDf)), dbc.Row(dcc.Graph(figure=graph_southDf))])

#             #         # dbc.Col(dcc.Graph(figure=graph_northDf), width=6),
#             #         # dbc.Col(dcc.Graph(figure=graph_cityDf), width=6),
#             #         # dbc.Col(dcc.Graph(figure=graph_southDf), width=6),
#             #     ]
#             # )
        
#         elif active_tab == "traffic":
#             return dbc.Row(
#                 [
#                     dbc.Col(dcc.Graph(figure=data["hist_1"]), width=6),
#                     dbc.Col(dcc.Graph(figure=data["hist_2"]), width=6),
#                 ]
#             )
#         elif active_tab == "size":
#             return dcc.Graph(figure=data["size"])
#     return "No tab selected"


# @app.callback(Output("store", "data"), [Input("button", "n_clicks")])
# def generate_graphs(n):
#     """
#     This callback generates three simple graphs from random data.
#     """
#     if not n:
#         # generate empty graphs when app loads
#         return {k: go.Figure(data=[]) for k in ["maps", "hist_1", "hist_2", "size"]}

#     # # simulate expensive graph generation process
#     # time.sleep(2)

#     # # generate 100 multivariate normal samples
#     # data = np.random.multivariate_normal([0, 0], [[1, 0.5], [0.5, 1]], 100)

#     # scatter = go.Figure(
#     #     data=[go.Scatter(x=data[:, 0], y=data[:, 1], mode="markers")]
#     # )

#     maps = px.scatter_mapbox(mapDf, lat="Lat", lon="Long", color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
#     hist_1 = go.Figure(data=[go.Histogram(x=data[:, 0])])
#     hist_2 = go.Figure(data=[go.Histogram(x=data[:, 1])])

#     vehicleSize = go.Figure(data=[go.Histogram(x=data[:,0])])

#     # save figures in a dictionary for sending to the dcc.Store
#     return {"maps": maps, "hist_1": hist_1, "hist_2": hist_2, "size":size}


# if __name__ == "__main__":
#     app.run_server(debug=True)

