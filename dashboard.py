import pandas as pd
import panel as pn 
import folium


def createGroup(f, zone):
    f1 = f[f['Zone']==zone]
    f1 = f1.groupby(['SensorID', 'variable', 'Zone', 'Month_Year'], as_index=False)['value'].sum()
    print(f1.head())
    return f1


df = pd.read_parquet(r'C:\Users\IyerA3\OneDrive - Vodafone Group\Personal\CambridgeshireTraffic-main\CambridgeSmartSensors\SensorData.parquet')
df.reset_index(inplace=True)
df['Date'] = df['Date_Time'].dt.date
df['Month_Year'] = df['Date_Time'].dt.to_period('M')

north = ['S20', 'S13', 'S19', 'S21', 'S18']
city = ['S10', 'S2', 'S41', 'S1', 'S4', 'S7', 'S15']
south = ['S12', 'S6', 'S14', 'S40', 'S3', 'S16']
df.loc[df['SensorID'].isin(north), 'Zone']='North'
df.loc[df['SensorID'].isin(city), 'Zone']='City'
df.loc[df['SensorID'].isin(south), 'Zone']='South'
print('Finished reading and creating zones')


mapDf = df[['SensorID', 'Lat', 'Long', 'Street location', 'Zone']].copy()
mapDf = mapDf.drop_duplicates()

m = folium.Map(location=[52.205276, 0.119167], zoom_start=12, control_scale=True)
for i, row in mapDf.iterrows():
    folium.Marker(row['Lat'], row['Long']).add_to(m)

pn.Column(m).servable()

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

