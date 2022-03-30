from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px


def getFrame(df, agg_func):
    if agg_func =='mean':
        frame = df.groupby(['Month_Year', 'Vehicle Type', 'Zone'], as_index=False)['value'].mean()
    elif agg_func=='sum':
        frame = df.groupby(['Month_Year', 'Vehicle Type', 'Zone'], as_index=False)['value'].sum()

    frame.sort_values(by='Month_Year', inplace=True)
    frame['Month_Year'] = frame['Month_Year'].dt.strftime('%B-%Y')
    return frame


def getDirection(df, agg_func):
    if agg_func =='mean':
        frame = df.groupby(['Month_Year', 'Vehicle Type', 'Zone', 'direction'], as_index=False)['value'].mean()
    elif agg_func=='sum':
        frame = df.groupby(['Month_Year', 'Vehicle Type', 'Zone', 'direction'], as_index=False)['value'].sum()

    frame.sort_values(by='Month_Year', inplace=True)
    frame['Month_Year'] = frame['Month_Year'].dt.strftime('%B-%Y')
    return frame


app = Dash(__name__)

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

df = pd.read_parquet(r'results/SensorData.parquet')
df.reset_index(inplace=True)
df['Month_Year'] = df['Date_Time'].dt.to_period('M')
df['day_of_week'] = df['Date_Time'].dt.dayofweek

north = ['S20', 'S13', 'S19', 'S21', 'S18']
city = ['S10', 'S2', 'S41', 'S1', 'S4', 'S7', 'S15']
south = ['S12', 'S6', 'S14', 'S40', 'S3', 'S16']
df.loc[df['SensorID'].isin(north), 'Zone'] = 'North'
df.loc[df['SensorID'].isin(city), 'Zone'] = 'City'
df.loc[df['SensorID'].isin(south), 'Zone'] = 'South'

d1 = {'Car':'Small Vehicles', 'Pedestrian':'Pedestrians and Cyclists', 'Cyclist':'Pedestrians and Cyclists', 'Motorbike':'Small Vehicles', 'Bus':'Large Vehicles', 'OGV1':'Large Vehicles', 'OGV2':'Large Vehicles', 'LGV':'Large Vehicles'}
df['Vehicle Type'] = df['variable'].map(d1)
print('Dataframe read and formatted')

mapDf = df[['SensorID', 'Lat', 'Long', 'Street location', 'Zone']].copy()
mapDf = mapDf.drop_duplicates()

p1 = px.scatter_mapbox(mapDf, lat='Lat', lon='Long', mapbox_style="open-street-map", zoom=10, color='Zone', hover_name='Street location')
p1.update_traces(marker={'size': 12})
p1.update_layout(title='Sensor locations', hovermode='closest', width=1000)

print('Map dataframe created')


northTraffic = df[df['Zone'] == 'North'][['SensorID', 'Month_Year', 'Vehicle Type', 'value', 'Zone', 'direction', 'day_of_week']]
northTrafficMean = getFrame(northTraffic, 'mean')
northTrafficSum = getFrame(northTraffic, 'sum')

northTrafficInwardSum = getDirection(northTraffic[northTraffic['direction'] == 'in'], 'sum')
northTrafficOutwardSum = getDirection(northTraffic[northTraffic['direction'] == 'out'], 'sum')

weekdayNorthTraffic = northTraffic[northTraffic['day_of_week'] < 5]
weekdayNorthTrafficSum = getDirection(weekdayNorthTraffic, 'sum')


cityTraffic = df[df['Zone'] == 'City'][['SensorID', 'Month_Year', 'Vehicle Type', 'value', 'Zone', 'direction', 'day_of_week']]
cityTrafficMean = getFrame(cityTraffic, 'mean')
cityTrafficSum = getFrame(cityTraffic, 'sum')

cityTrafficInwardSum = getDirection(cityTraffic[cityTraffic['direction'] == 'in'], 'sum')
cityTrafficOutwardSum = getDirection(cityTraffic[cityTraffic['direction'] == 'out'], 'sum')


weekdayCityTraffic = cityTraffic[cityTraffic['day_of_week'] < 5]
weekdayCityTrafficSum = getDirection(weekdayCityTraffic, 'sum')


southTraffic = df[df['Zone'] == 'South'][['SensorID', 'Month_Year', 'Vehicle Type', 'value', 'Zone', 'direction', 'day_of_week']]
southTrafficMean = getFrame(southTraffic, 'mean')
southTrafficSum = getFrame(southTraffic, 'sum')

southTrafficInwardSum = getDirection(southTraffic[southTraffic['direction'] == 'in'], 'sum')
southTrafficOutwardSum = getDirection(southTraffic[southTraffic['direction'] == 'out'], 'sum')

weekdaySouthTraffic = southTraffic[southTraffic['day_of_week'] < 5]
weekdaySouthTrafficSum = getDirection(weekdaySouthTraffic, 'sum')



totalTrafficMean = pd.concat([northTrafficMean, cityTrafficMean, southTrafficMean], ignore_index=True)
totalTrafficSum = pd.concat([northTrafficSum, cityTrafficSum, southTrafficSum], ignore_index=True)
totalDirectionalTraffic = pd.concat([northTrafficInwardSum, northTrafficOutwardSum, cityTrafficInwardSum,\
                                     cityTrafficOutwardSum, southTrafficInwardSum, southTrafficOutwardSum],\
                                    ignore_index=True)
totalWeekdayTraffic = pd.concat([weekdayNorthTrafficSum, weekdayCityTrafficSum, weekdaySouthTrafficSum], ignore_index=True)


print('Total and mean traffic per zone computed')

fig1 = px.area(totalTrafficMean, x="Month_Year", y="value", color="Vehicle Type", facet_col="Zone", width=1000, title='Average traffic per month')
fig2 = px.area(totalTrafficSum, x="Month_Year", y="value", color="Vehicle Type", facet_col="Zone", width=1000, title='Total traffic per month')
fig3 = px.area(totalDirectionalTraffic, x="Month_Year", y="value", color="direction", facet_row="Zone", facet_col='Vehicle Type',width=1000, title='Traffic per direction')
fig4 = px.area(totalWeekdayTraffic, x="Month_Year", y="value", color="Vehicle Type", facet_row="Zone", facet_col='direction',width=1000, title='Weekday Traffic per zone')

print('Figures drawn')

app.layout = html.Div([
    dcc.Tabs(id="tabs-styled-with-inline", value='tab-1', children=[
        dcc.Tab(label='Location and summary', value='tab-1', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Incoming vs outgoing traffic', value='tab-2', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Weekend vs weekday traffic', value='tab-3', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Tab 4', value='tab-4', style=tab_style, selected_style=tab_selected_style),
    ], style=tabs_styles),
    html.Div(id='tabs-content-inline')
])

@app.callback(Output('tabs-content-inline', 'children'),
              Input('tabs-styled-with-inline', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            dcc.Graph(figure=p1),
            dcc.Graph(figure=fig1),
            dcc.Graph(figure=fig2)
        ])
    elif tab == 'tab-2':
        return html.Div([
            dcc.Graph(figure=fig3)
        ])
    elif tab == 'tab-3':
        return html.Div([
            dcc.Graph(figure=fig4)
        ])
    elif tab == 'tab-4':
        return html.Div([
            html.H3('Tab content 4')
        ])

if __name__ == '__main__':
    app.run_server(debug=True)