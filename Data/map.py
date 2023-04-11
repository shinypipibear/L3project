import urllib.request, json
import urllib.parse as urlparse
from datetime import datetime
from convertbng.util import convert_bng
import pandas as pd
import pickle
import folium
import json
import sys

dir_endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
road_class_endpoint = 'https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?'
speed_endpoint = 'https://dev.virtualearth.net/REST/v1/Routes/SnapToRoad?'

google_api_key = 'AIzaSyCPoOaOxZiot3-xorCLtJoGWg8avp_ScZY'
tomtom_api_key = '4Jyrf3MYTkjfr8AqDreqLTf5aP4usS7j'
bing_api_key = 'Ar8PTYp49vArB0X7U2236MQPDVUVVlfOQpybRgTwWcZKMZycZHcE_s77xCZxzjvP'

origin = 'Canary+Wharf'
destination = 'Buckingham+Palace'
# if len(sys.argv) == 1:
#     origin = 'Canary+Wharf'
#     destination = 'Buckingham+Palace'
# else:
#     script, origin, destination = sys.argv

departure_time = datetime.now()

road_class_dic = {
    "FRC0": 1,
    "FRC1": 2,
    "FRC2": 3,
    "FRC3": 5,
    "FRC4": 4,
    "FRC5": 4,
    "FRC6": 5
}

day_of_week = 2
light_conditions = 1
weather_conditions = 1
road_surface_conditions = 1
special_conditions_at_site = 0
urban_or_rural_area = 1
time_slot = departure_time.hour  # time may change
vehicle_type = 9
sex_of_driver = 1
age_band_of_driver = 5
engine_capacity_cc = 1390
driver_home_area_type = 1


def decode_polyline(polyline):
    """Decodes a Polyline string into a list of lat/lng dicts.
    See the developer docs for a detailed description of this encoding:
    https://developers.google.com/maps/documentation/utilities/polylinealgorithm
    :param polyline: An encoded polyline
    :type polyline: string
    :rtype: list of dicts with lat/lng keys
    """
    points = []
    index = lat = lng = 0

    while index < len(polyline):
        result = 1
        shift = 0
        while True:
            b = ord(polyline[index]) - 63 - 1
            index += 1
            result += b << shift
            shift += 5
            if b < 0x1f:
                break
        lat += (~result >> 1) if (result & 1) != 0 else (result >> 1)

        result = 1
        shift = 0
        while True:
            b = ord(polyline[index]) - 63 - 1
            index += 1
            result += b << shift
            shift += 5
            if b < 0x1f:
                break
        lng += ~(result >> 1) if (result & 1) != 0 else (result >> 1)

        points.append((lat * 1e-5, lng * 1e-5))

    return points


def pred(start, end):
    global light_conditions, weather_conditions, road_surface_conditions, special_conditions_at_site, urban_or_rural_area, time_slot, vehicle_type, sex_of_driver, age_band_of_driver, engine_capacity_cc, driver_home_area_type
    nav_request = 'origin={}&destination={}&departure_time={}&key={}'.format(start, end, int(round(departure_time.timestamp())),google_api_key)
    dir_request = dir_endpoint + nav_request
    dir_response = urllib.request.urlopen(dir_request).read()
    directions = json.loads(dir_response)
    routes = directions['routes']
    print(dir_request)
    print(len(routes))
    legs = routes[0]['legs']
    steps = legs[0]['steps']
    over_distance = legs[0]['distance']['text']
    over_duration = legs[0]['duration']['text']
    data = []
    for i in steps:
        latitude = i['end_location']['lat']
        longitude = i['end_location']['lng']

        latitude_1 = i['start_location']['lat']
        longitude_1 = i['start_location']['lng']

        location_easting_osgr = convert_bng(longitude, latitude)[0][0]
        location_northing_osgr = convert_bng(longitude, latitude)[1][0]

        location_easting_osgr_1 = convert_bng(longitude_1, latitude_1)[0][0]
        location_northing_osgr_1 = convert_bng(longitude_1, latitude_1)[1][0]

        road_class_request = road_class_endpoint + 'key=' + urlparse.quote(tomtom_api_key) + '&point=' + urlparse.quote(
            str(latitude)) + ',' + urlparse.quote(str(longitude))
        road_class_response = urllib.request.urlopen(road_class_request).read()
        road_class = json.loads(road_class_response)
        frc = road_class['flowSegmentData']['frc']
        first_road_class = road_class_dic[frc]

        road_class_request_1 = road_class_endpoint + 'key=' + urlparse.quote(
            tomtom_api_key) + '&point=' + urlparse.quote(str(latitude_1)) + ',' + urlparse.quote(str(longitude_1))
        road_class_response_1 = urllib.request.urlopen(road_class_request_1).read()
        road_class_1 = json.loads(road_class_response_1)
        frc_1 = road_class_1['flowSegmentData']['frc']
        second_road_class = road_class_dic[frc_1]

        speed_limit_request = speed_endpoint + 'points=' + urlparse.quote(str(latitude)) + ',' + urlparse.quote(
            str(longitude)) + ';' + urlparse.quote(str(latitude_1)) + ',' + urlparse.quote(
            str(longitude_1)) + '&IncludeSpeedLimit=true&speedUnit=KPH&travelMode=driving&key=' + urlparse.quote(
            bing_api_key)

        speed_limit_response = urllib.request.urlopen(speed_limit_request).read()
        speed_limit_data = json.loads(speed_limit_response)
        speed_limit = speed_limit_data['resourceSets'][0]['resources'][0]['snappedPoints'][0]['speedLimit']
        speed_limit_1 = speed_limit_data['resourceSets'][0]['resources'][0]['snappedPoints'][1]['speedLimit']

        light_conditions = light_conditions
        weather_conditions = weather_conditions
        road_surface_conditions = road_surface_conditions
        special_conditions_at_site = special_conditions_at_site
        urban_or_rural_area = urban_or_rural_area
        time_slot = time_slot
        vehicle_type = vehicle_type
        sex_of_driver = sex_of_driver
        age_band_of_driver = age_band_of_driver
        engine_capacity_cc = engine_capacity_cc
        driver_home_area_type = driver_home_area_type
        end_columns = [location_easting_osgr, location_northing_osgr, longitude, latitude, day_of_week,
                       first_road_class,
                       speed_limit, second_road_class, light_conditions, weather_conditions, road_surface_conditions,
                       special_conditions_at_site, urban_or_rural_area, time_slot, vehicle_type, sex_of_driver,
                       age_band_of_driver, engine_capacity_cc, driver_home_area_type]
        start_columns = [location_easting_osgr_1, location_northing_osgr_1, longitude_1, latitude_1, day_of_week,
                         first_road_class, speed_limit_1, second_road_class, light_conditions, weather_conditions,
                         road_surface_conditions, special_conditions_at_site, urban_or_rural_area, time_slot,
                         vehicle_type,
                         sex_of_driver, age_band_of_driver, engine_capacity_cc, driver_home_area_type]
        data.append(end_columns)
        data.append(start_columns)

    df = pd.DataFrame(data, columns=['location_easting_osgr', 'location_northing_osgr', 'longitude', 'latitude',
                                     'day_of_week', 'first_road_class', 'speed_limit', 'second_road_class',
                                     'light_conditions', 'weather_conditions', 'road_surface_conditions',
                                     'special_conditions_at_site', 'urban_or_rural_area', 'time_slot', 'vehicle_type',
                                     'sex_of_driver', 'age_band_of_driver', 'engine_capacity_cc',
                                     'driver_home_area_type'])
    filename = 'finalized_model.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    prediction = loaded_model.predict(df)
    accident_severity = prediction
    df['accident_severity'] = accident_severity
    return over_distance, over_duration, int(df.loc[:, 'accident_severity'].mean()), legs, steps, df,


def ploy(legs, steps, df):
    m = folium.Map(location=[51.509865, -0.118092], zoom_start=13, control_scale=True, tiles="cartodbpositron")
    origin_point = (legs[0]['start_location']['lat'], legs[0]['start_location']['lng'])
    destination_point = (legs[0]['end_location']['lat'], legs[0]['end_location']['lng'])
    color_list = {
        1.0: "#FF0000",
        2.0: "#FFFF00",
        3.0: "#00FF00"
    }
    for step in steps:
        start_loc = step['start_location']
        end_loc = step['end_location']
        start_row = df.loc[(df['longitude'] == start_loc['lng']) | (df['latitude'] == start_loc['lat'])]
        end_row = df.loc[(df['longitude'] == end_loc['lng']) | (df['latitude'] == end_loc['lat'])]
        accident_severity_start = start_row.iloc[0]['accident_severity']
        accident_severity_end = end_row.iloc[0]['accident_severity']
        accident_severity = (accident_severity_start + accident_severity_end) // 2
        distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>" + str(
            step['distance']['text']) + "</strong>" + "</h4></b>"
        duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>" + str(
            step['duration']['text']) + "</strong>" + "</h4></b>"
        severity_txt = "<h4> <b>Severity :&nbsp" + "<strong>" + str(accident_severity) + "</strong>" + "</h4></b>"
        decoded = decode_polyline(step['polyline']['points'])
        folium.PolyLine(decoded, color=color_list[accident_severity], weight=5, opacity=1).add_child(
            folium.Popup(distance_txt + duration_txt + severity_txt, max_width=300)).add_to(m)

    folium.Marker(origin_point, icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(destination_point, icon=folium.Icon(color="red")).add_to(m)

    m.save('./route_map.html')


state = True
while state:
    a_distance, a_duration, a_severity, a_legs, a_steps, a_df, = pred(origin, destination)
    # b_distance, b_duration, b_severity, b_legs, b_steps, b_df = pred(origin, destination, traffic_model='pessimistic')
    # c_distance, c_duration, c_severity, c_legs, c_steps, c_df = pred(origin, destination, traffic_model='optimistic')
    print("There are two routes available")
    print(f"A distance: {a_distance}, duration: {a_duration}, severity: {a_severity}")
    # print(f"B distance: {b_distance}, duration: {b_duration}, severity: {b_severity}")
    # print(f"c distance: {c_distance}, duration: {c_duration}, severity: {c_severity}")
    which_route = input("Please choose which route you'd like to take: ")
    if which_route == 'a':
        ploy(a_legs, a_steps, a_df)
    # elif which_route == 'b':
    #     ploy(b_legs, b_steps, b_df)
    # else:
    #     ploy(c_legs, c_steps, c_df)
    print("Map created")
    q = input("Please enter q to quit")
    if q == 'q':
        state = False
