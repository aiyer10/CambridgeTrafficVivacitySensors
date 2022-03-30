import pandas as pd, numpy as np
import os, glob


locations = pd.read_csv(r'data/Locations.csv')
locations['SensorID'] = r'S'+locations['Sensor Reference'].astype(str)
print(locations.head())

d = pd.DataFrame()
for f in glob.glob(os.path.join(r'data/', 'S*.csv')):
	print(f.split('\\')[-1])
	df = pd.read_csv(f, usecols=['Date','Time', 'countlineName', 'direction', 'Car', 'Pedestrian', 'Cyclist', 'Motorbike', 'Bus', 'OGV1','OGV2','LGV'], parse_dates=[['Date','Time']])
	df['SensorID'] = df['countlineName'].str.extract(r'(S[^_]*)', expand=True)
	
	df1 = pd.merge(df, locations)[['Date_Time','Lat','Long', 'Street location', 'countlineName', 'direction' , 'Car', 'Pedestrian' ,'Cyclist', 'Motorbike', 'Bus', 'OGV1', 'OGV2', 'LGV', 'SensorID']]
	df1 = pd.melt(df1, id_vars=['Date_Time','Lat','Long', 'Street location', 'countlineName', 'direction', 'SensorID'], value_vars=['Car', 'Pedestrian' ,'Cyclist', 'Motorbike', 'Bus', 'OGV1', 'OGV2', 'LGV'])
	df1['Street location'] = df1['Street location'].astype('category')
	df1['countlineName'] = df1['countlineName'].astype('category')
	df1['direction'] = df1['direction'].astype('category')
	df1['variable'] = df1['variable'].astype('category')
	df1['weekday'] = pd.Series(df1['Date_Time']).dt.day_name()
	d = pd.concat([d, df1], axis=0)
	print(df1.head())
print(d['weekday'].unique())	
d.to_parquet(r'results/SensorData.parquet', index=None, engine='fastparquet')
# d.to_csv(r'C:\Users\IyerA3\OneDrive - Vodafone Group\Personal\CambridgeshireTraffic-main\CambridgeSmartSensors\SensorData.csv', index=None)
