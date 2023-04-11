import pandas as pd
import numpy as np
from sklearn import preprocessing

accident_df = pd.read_csv('dataset/dft-road-casualty-statistics-accident-2021.csv', low_memory=False)
# accident_df_2 = pd.read_csv('dataset/dft-road-casualty-statistics-accident-2020.csv', low_memory=False)
# accident_df_3 = pd.read_csv('dataset/dft-road-casualty-statistics-accident-2019.csv', low_memory=False)
# accident_frame = [accident_df_1, accident_df_2, accident_df_3]
# accident_df = pd.concat(accident_frame)

vehicle_df = pd.read_csv('dataset/dft-road-casualty-statistics-vehicle-2021.csv', low_memory=False)
# vehicle_df_2 = pd.read_csv('dataset/dft-road-casualty-statistics-vehicle-2020.csv', low_memory=False)
# vehicle_df_3 = pd.read_csv('dataset/dft-road-casualty-statistics-vehicle-2019.csv', low_memory=False)
# vehicle_frame = [vehicle_df_1, vehicle_df_2, vehicle_df_3]
# vehicle_df = pd.concat(vehicle_frame)

# weather_df = pd.read_csv('dataset/weather_01_31.csv', skiprows=3)
# crime_df_1 = pd.read_csv('dataset/2021-01-metropolitan-street.csv')
# crime_df_2 = pd.read_csv('dataset/2021-01-city-of-london-street.csv')

# accident_df = accident_df.loc[(accident_df['police_force'] == 1) | (accident_df['police_force'] == 48)]
accident_df = accident_df.drop(accident_df.columns[[9, 10, 18, 21, 22, 24, 25, 26, 31, 33, 34, 35]], axis=1)
accident_df['date_time'] = accident_df['date']+" "+accident_df['time']
accident_df['date_time'] = pd.to_datetime(accident_df.date_time)
hours = accident_df['date_time'].dt.hour
accident_df['time_slot'] = hours.astype(str) # may 2hrs into one slot
accident_df.drop(['date','time', 'date_time'], axis=1, inplace=True)
accident_df.dropna(inplace=True)
accident_df.to_csv(r'accident.csv', index=False)

vehicle_df = vehicle_df[vehicle_df.sex_of_driver != -1]
vehicle_df = vehicle_df[vehicle_df.sex_of_driver != 3]
vehicle_df = vehicle_df[vehicle_df.age_band_of_driver != -1]
vehicle_df = vehicle_df[vehicle_df.age_of_driver >= 17]
vehicle_df = vehicle_df[vehicle_df.age_of_vehicle != -1]
vehicle_df = vehicle_df[vehicle_df.driver_home_area_type != -1]
vehicle_df = vehicle_df[vehicle_df.engine_capacity_cc != -1]
vehicle_df = vehicle_df.drop(vehicle_df.columns[[0, 1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 22, 24, 25, 27]], axis=1)
acc_veh_df = pd.merge(accident_df, vehicle_df, on=['accident_reference'])
# acc_veh_df = acc_veh_df.loc[(acc_veh_df['police_force'] == 1) | (acc_veh_df['police_force'] == 48)]
acc_veh_df.drop(['age_of_driver','age_of_vehicle'], axis=1, inplace=True)
# acc_veh_df['engine_capacity_cc'] = preprocessing.normalize([np.array(acc_veh_df['engine_capacity_cc'])])[0]
# acc_veh_df['age_of_driver'] = preprocessing.normalize([np.array(acc_veh_df['age_of_driver'])])[0]
# acc_veh_df['age_of_vehicle'] = preprocessing.normalize([np.array(acc_veh_df['age_of_vehicle'])])[0]
acc_veh_df = acc_veh_df.drop(acc_veh_df.columns[[1, 7, 10, 11, 12]], axis=1)
acc_veh_df.to_csv(r'acc_veh.csv', index=False)

# weather_sum_df = weather_df.iloc[-32:-1]
# weather_sum_df = weather_sum_df.iloc[:,:-1]
# new_names = weather_sum_df.iloc[0]
# weather_sum_df = weather_sum_df[1:]
# weather_sum_df.columns = new_names
#
# weather_df = weather_df.iloc[:-33]
# weather_df.to_csv(r'weather.csv', index=False)
#
# frames = [crime_df_1, crime_df_2]
# crime_df = pd.concat(frames, keys=["metropolitan", "city_of_london"])
# crime_df.drop(crime_df[crime_df.Location == "No Location"].index, inplace=True)
# crime_df.drop(crime_df[crime_df.iloc[:, 9] == "Burglary"].index, inplace=True)
# crime_df.drop(crime_df[crime_df.iloc[:, 9] == "Public order"].index, inplace=True)
# crime_df.drop(crime_df[crime_df.iloc[:, 9] == "Drugs"].index, inplace=True)
# crime_df.to_csv(r'crime.csv', index=False)
#
# hospital = pd.read_json('dataset/hospital.json', orient='records')
# hospital = hospital.drop(hospital.columns[[0, 3, 4, 9, 10]], axis=1)
# hospital.to_csv(r'hospital.csv', index=False)
#
# school = pd.read_json('dataset/school.json', orient='records')
# school = school.drop(school.columns[[0, 3, 4, 9, 10]], axis=1)
# school.to_csv(r'school.csv', index=False)
