import numpy as np
import pandas as pd
import gmaps.datasets
import plotly.express as px
from matplotlib import pyplot as plt, dates as mdates
import seaborn as sns

# accident = pd.read_csv('accident.csv')
# guide = pd.read_csv('dataset/Road-Safety-Open-Dataset-Data-Guide.csv')
# borough_names = accident.local_authority_ons_district.unique()
# borough_names_dict = {}
#
# for i in borough_names:
#     guide_borough_name = guide.loc[guide['code/format'] == i]
#     name = guide_borough_name.iloc[0].label
#     borough_names_dict.update({i: name})
#
# borough_accident = accident['local_authority_ons_district'].value_counts().to_frame()
# borough_accident['borough_name'] = borough_accident.index
# borough_accident = borough_accident.replace({"borough_name": borough_names_dict})
#
# borough_accident.rename({'local_authority_ons_district': 'total_accidents'}, axis=1, inplace=True)
#
# time = accident['time'].value_counts().to_frame()
# time.rename({'time':'count'}, axis=1, inplace=True)
# time['time'] = time.index
# time["time"] = pd.to_datetime(time["time"])
#
# # graph
# # sns.set_context('paper')
# # ax=sns.lineplot(x = "time", y = "count", data = time)
# # ax.set_xlim([pd.to_datetime('2022-12-06 00:00:00'),
# #              pd.to_datetime('2022-12-06 23:59:59')])
# # ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
# # plt.title('Accident by time')
# # plt.show()
#
# accident = accident.drop(accident[accident.weather_conditions == 8].index)
# accident = accident.drop(accident[accident.weather_conditions == 9].index)
# weather = accident['weather_conditions'].value_counts().to_frame()
# print(weather)
# sns.set_context('paper')
# sns.countplot(x = 'weather_conditions', hue = 'accident_severity', data = accident, palette = 'magma')
# plt.title('Accident by weather')
# plt.show()
#
# slight = accident.loc[accident['accident_severity'] == 3]
# slight = slight['local_authority_ons_district'].value_counts().to_frame()
# slight['borough_code'] = slight.index
# slight = slight.replace({"borough_code":borough_names_dict})
#
# serious = accident.loc[accident['accident_severity'] == 2]
# serious = serious['local_authority_ons_district'].value_counts(normalize=True).to_frame()
# serious['borough_code'] = serious.index
# serious = serious.replace({"borough_code":borough_names_dict})
#
# fatal = accident.loc[accident['accident_severity'] == 1]
# fatal = fatal['local_authority_ons_district'].value_counts(normalize=True).to_frame()
# fatal['borough_code'] = fatal.index
# fatal = fatal.replace({"borough_code":borough_names_dict})
#
# # heatmap
# # color_scale = [(0, 'blue'), (1,'red')]
# # fig = px.scatter_mapbox(accident,
# #                         lat="latitude",
# #                         lon="longitude",
# #                         hover_name="local_authority_ons_district",
# #                         hover_data=["local_authority_ons_district", "accident_severity"],
# #                         color="accident_severity",
# #                         size="accident_severity",
# #                         zoom=8,
# #                         height=800,
# #                         width=800)
# # fig.update_layout(mapbox_style="open-street-map")
# # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
# # fig.show()
# # api_key = "AIzaSyCPoOaOxZiot3-xorCLtJoGWg8avp_ScZY"
# # Lon = np.arange(-0.51, 0.30, 0.008181)
# # Lat = np.arange(51.29, 51.70, 0.004141)
# # accident_counts = np.zeros((100, 100))
# # for a in range(len(accident)):
# #     for b1 in range(100):
# #         if Lat[b1]-0.00405 <= accident['latitude'].values[a] < Lat[b1]+0.00405:
# #             for b2 in range(100):
# #                 if Lon[b2]-0.00205<= accident['longitude'].values[a] < Lon[b2]+0.00205:
# #                     accident_counts[b1, b2] += 1
# # gmaps.configure(api_key="AIzaSyCPoOaOxZiot3-xorCLtJoGWg8avp_ScZY")
# # longitude_values = [Lon, ]*100
# # latitude_values = np.repeat(Lat,100)
# # accident_counts.resize((10100,))
# # heatmap_data = {'Counts': accident_counts, 'latitude': latitude_values, 'longitude' : np.concatenate(longitude_values)}
# # print(len(heatmap_data['longitude']))
# # print(len(heatmap_data['latitude']))
# # df = pd.DataFrame(data=heatmap_data)
# # locations = df[['latitude', 'longitude']]
# # weights = df['Counts']
# # fig = gmaps.figure()
# # heatmap_layer = gmaps.heatmap_layer(locations, weights=weights)
# # fig.add_layer(gmaps.heatmap_layer(locations, weights=weights))
# # fig