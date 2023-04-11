import pandas as pd
import numpy as np
import glob
import os
import logging

path = os.getcwd() # use your path
logging.warning(path)
all_files = glob.glob(os.path.join(path, "crime_data/crime_data/*.csv"))
crime_df = pd.concat((pd.read_csv(f) for f in all_files), ignore_index=True)

crime_df.columns = crime_df.columns.str.replace(' ', '_')
crime_df.drop(crime_df[crime_df.Location == "No Location"].index, inplace=True)
crime_df.drop(crime_df[crime_df.Crime_type == "Violence and sexual offences"].index, inplace=True)
crime_df.drop(crime_df[crime_df.Crime_type == "Bicycle theft"].index, inplace=True)
crime_df.drop(crime_df[crime_df.Crime_type == "Other crime"].index, inplace=True)
crime_df.drop(crime_df[crime_df.Crime_type == "Drugs"].index, inplace=True)
crime_df.drop(crime_df[crime_df.Crime_type == "Shoplifting"].index, inplace=True)
crime_df.drop(crime_df[crime_df.Crime_type == "Burglary"].index, inplace=True)
crime_df.drop(crime_df[crime_df.Crime_type == "Possession of weapons"].index, inplace=True)

Lon = np.arange(-0.51, 0.30, 0.0081)
Lat = np.arange(51.29, 51.70, 0.0041)
crime_counts = np.zeros((100, 100))
for a in range(len(crime_df)):
    for b1 in range(100):
        if Lat[b1] - 0.00205 <= crime_df['Latitude'].values[a] < Lat[b1] + 0.00205:
            for b2 in range(100):
                if Lon[b2] - 0.00405 <= crime_df['Longitude'].values[a] < Lon[b2] + 0.00405:
                    crime_counts[b1, b2] += 1

longitude_values = [Lon, ]*100
latitude_values = np.repeat(Lat,100)
crime_counts.resize((10100,))
heatmap_data = {'Counts': crime_counts, 'latitude': latitude_values, 'longitude' : np.concatenate(longitude_values)}
df = pd.DataFrame(data=heatmap_data)
df.to_csv("crime_data.csv", index=False)
counts_values = [i for i in df.Counts.values if i != 0]
x = np.quantile(counts_values, [0,0.25,0.5,0.75,1])
df["Crime_level"] = np.zeros((10100,), dtype=int)
logging.warning(x)
logging.warning('done')
for i in df.index:
    if df["Counts"][i] <= x[2]:
        df.iloc[i, 3] = 3
    elif x[2] < df["Counts"][i] <= x[3]:
        df.iloc[i, 3] = 2
    elif x[3] < df["Counts"][i] <= x[4]:
        df.iloc[i, 3] = 1
    else:
        df.iloc[i, 3] = 0
df.to_csv("crime_level_data.csv", index=False)