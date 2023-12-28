from django.shortcuts import render, redirect
from .models import User_input, User_option
from .forms import User_inputForm, User_optionForm
from convertbng.util import convert_bng
import urllib.parse as urlparse
import folium
import datetime
import pandas as pd
import pickle
import aiohttp
import asyncio
import time
import logging
import urllib
import json

# get user's profile data
def index(request):
    if request.method == 'POST':
        form = User_inputForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/map/option')
    else:
        form = User_inputForm()

    # create map object
    m = folium.Map(location=[51.509865, -0.118092], zoom_start=13, control_scale=True, tiles="cartodbpositron")
    # get html representation
    m = m._repr_html_()
    context = {
        'm': m,
        'form': form,
    }
    return render(request, 'index.html', context)


# get user's origin & destination
def option(request):
    if request.method == 'POST':
        form_option = User_optionForm(request.POST)
        if form_option.is_valid():
            form_option.save()
            return redirect('/map/show')
    else:
        form_option = User_optionForm()
    # create map object
    m = folium.Map(location=[51.509865, -0.118092], zoom_start=13, control_scale=True, tiles="cartodbpositron")
    # get html representation
    m = m._repr_html_()
    context = {
        'm': m,
        'form_option': form_option,
    }
    return render(request, 'option.html', context)


# prediction
road_class_dic = {
    "FRC0": 1,
    "FRC1": 2,
    "FRC2": 3,
    "FRC3": 5,
    "FRC4": 4,
    "FRC5": 4,
    "FRC6": 5,
    "FRC7": 5,
    "FRC8": 6
}

# api
dir_endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
road_class_endpoint = 'https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?'
speed_endpoint = 'https://dev.virtualearth.net/REST/v1/Routes/SnapToRoad?'

google_api_key = 'AIzaSyCPoOaOxZiot3-xorCLtJoGWg8avp_ScZY'
tomtom_api_key = '4Jyrf3MYTkjfr8AqDreqLTf5aP4usS7j'
bing_api_key = 'Ar8PTYp49vArB0X7U2236MQPDVUVVlfOQpybRgTwWcZKMZycZHcE_s77xCZxzjvP'


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


crime_df = pd.read_csv('/Users/shinypipibear/PycharmProjects/L3project_interface/map/crime_level_data.csv')


# prediction async function
async def pred(directions):
    async with aiohttp.ClientSession() as session:
        routes = directions['routes']
        legs = routes[0]['legs']
        steps = legs[0]['steps']
        tasks = []
        for i in steps:
            task = asyncio.ensure_future(get_pred(session, i))
            task_1 = asyncio.ensure_future(get_pred_1(session, i))
            tasks.append(task)
            tasks.append(task_1)

        data = await asyncio.gather(*tasks)

        df = pd.DataFrame(data, columns=['location_easting_osgr', 'location_northing_osgr', 'longitude', 'latitude',
                                         'day_of_week', 'first_road_class', 'speed_limit', 'second_road_class',
                                         'light_conditions', 'weather_conditions', 'road_surface_conditions',
                                         'special_conditions_at_site', 'urban_or_rural_area', 'time_slot',
                                         'vehicle_type',
                                         'sex_of_driver', 'age_band_of_driver', 'engine_capacity_cc',
                                         'driver_home_area_type','current_speed', 'current_travel_time', 'free_flow_travel_time'])
        filename = '/Users/shinypipibear/PycharmProjects/L3project_interface/map/finalized_model.sav'
        loaded_model = pickle.load(open(filename, 'rb'))
        prediction = loaded_model.predict(df[['location_easting_osgr', 'location_northing_osgr', 'longitude', 'latitude',
                                         'day_of_week', 'first_road_class', 'speed_limit', 'second_road_class',
                                         'light_conditions', 'weather_conditions', 'road_surface_conditions',
                                         'special_conditions_at_site', 'urban_or_rural_area', 'time_slot',
                                         'vehicle_type',
                                         'sex_of_driver', 'age_band_of_driver', 'engine_capacity_cc',
                                         'driver_home_area_type']])
        accident_severity = prediction
        df['accident_severity'] = accident_severity

        m = folium.Map(location=[51.509865, -0.118092], zoom_start=13, control_scale=True, tiles="cartodbpositron")
        origin_point = (legs[0]['start_location']['lat'], legs[0]['start_location']['lng'])
        destination_point = (legs[0]['end_location']['lat'], legs[0]['end_location']['lng'])
        color_list = {
            600.0: "#f07d02",
            1200.0: "#e60000",
            1800.0: "#9e1313 "
        }
        for step in steps:
            start_loc = step['start_location']
            end_loc = step['end_location']
            start_row = df.loc[(df['longitude'] == start_loc['lng']) | (df['latitude'] == start_loc['lat'])]
            end_row = df.loc[(df['longitude'] == end_loc['lng']) | (df['latitude'] == end_loc['lat'])]
            current_travel_time = start_row.iloc[0]['current_travel_time']
            free_flow_travel_time = start_row.iloc[0]['free_flow_travel_time']
            traffic_delay = current_travel_time-free_flow_travel_time
            accident_severity_start = start_row.iloc[0]['accident_severity']
            accident_severity_end = end_row.iloc[0]['accident_severity']
            accident_severity = (accident_severity_start + accident_severity_end) // 2
            logging.warning(start_loc['lat'])
            crime_data = crime_df.loc[(crime_df['latitude'] <= start_loc['lat'] + 0.00205) & (start_loc['lat'] - 0.00205 < crime_df['latitude'])
                                      & (crime_df['longitude'] <= start_loc['lng'] + 0.00405) & (start_loc['lng'] - 0.00405 < crime_df['longitude'])]
            logging.warning(crime_data)
            crime_level = crime_data['Crime_level'].values
            distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>" + str(
                step['distance']['text']) + "</strong>" + "</h4></b>"
            duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>" + str(
                step['duration']['text']) + "</strong>" + "</h4></b>"
            severity_txt = "<h4> <b>Severity :&nbsp" + "<strong>" + str(accident_severity) + "</strong>" + "</h4></b>"
            current_speed_txt = "<h4> <b>Travel speed :&nbsp" + "<strong>" + str(start_row.iloc[0]['current_speed']) + " kmph</strong>" + "</h4></b>"
            current_travel_time_txt = "<h4> <b>Travel time :&nbsp" + "<strong>" + str(
                start_row.iloc[0]['current_travel_time']) + " seconds</strong>" + "</h4></b>"
            crime_txt = "<h4> <b>Crime level:&nbsp" + "<strong>" + str(crime_level) + "</strong>" + "</h4></b>"
            decoded = decode_polyline(step['polyline']['points'])
            # for key, value in color_list.items():
            #     if traffic_delay > key:
            #         color = value
            #     else:
            #         color = "#87cb54"
            if accident_severity == 3:
                color = "#87cb54"
            elif accident_severity == 2:
                color = "#FFFF00"
            else:
                color = "#FF0000"
            folium.PolyLine(decoded, color=color, weight=5, opacity=1).add_child(
                folium.Popup(distance_txt + duration_txt + severity_txt + current_speed_txt + current_travel_time_txt + crime_txt, max_width=300)).add_to(m)

        folium.Marker(origin_point, icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(destination_point, icon=folium.Icon(color="red")).add_to(m)

        return m, int(df.loc[:, 'accident_severity'].mean())


# getting api end point data
async def get_pred(session, i):
    latitude = i['end_location']['lat']
    longitude = i['end_location']['lng']

    latitude_1 = i['start_location']['lat']
    longitude_1 = i['start_location']['lng']

    location_easting_osgr = convert_bng(longitude, latitude)[0][0]
    location_northing_osgr = convert_bng(longitude, latitude)[1][0]

    tasks = [asyncio.ensure_future(get_road(session, latitude, longitude)),
             asyncio.ensure_future(get_road(session, latitude_1, longitude_1)),
             asyncio.ensure_future(get_speed_limit(session, latitude, longitude))]

    results = await asyncio.gather(*tasks)
    first_road_class = road_class_dic[results[0]['frc']]
    second_road_class = road_class_dic[results[1]['frc']]
    current_speed = results[0]['currentSpeed']
    current_travel_time = results[0]['currentTravelTime']
    free_flow_travel_time = results[0]['freeFlowTravelTime']
    end_columns = [location_easting_osgr, location_northing_osgr, longitude, latitude, day_of_week,
                   first_road_class, results[2], second_road_class, light_conditions, weather_conditions,
                   road_surface_conditions, special_conditions_at_site, urban_or_rural_area, time_slot,
                   vehicle_type, sex_of_driver, age_band_of_driver, engine_capacity_cc, driver_home_area_type,
                   current_speed, current_travel_time, free_flow_travel_time]
    return end_columns


# getting api data start point data
async def get_pred_1(session, i):
    latitude = i['end_location']['lat']
    longitude = i['end_location']['lng']

    latitude_1 = i['start_location']['lat']
    longitude_1 = i['start_location']['lng']

    location_easting_osgr_1 = convert_bng(longitude_1, latitude_1)[0][0]
    location_northing_osgr_1 = convert_bng(longitude_1, latitude_1)[1][0]

    tasks = [asyncio.ensure_future(get_road(session, latitude, longitude)),
             asyncio.ensure_future(get_road(session, latitude_1, longitude_1)),
             asyncio.ensure_future(get_speed_limit(session, latitude_1, longitude_1))]

    results = await asyncio.gather(*tasks)
    first_road_class = road_class_dic[results[0]['frc']]
    second_road_class = road_class_dic[results[1]['frc']]
    current_speed = results[0]['currentSpeed']
    current_travel_time = results[0]['currentTravelTime']
    free_flow_travel_time = results[0]['freeFlowTravelTime']
    start_columns = [location_easting_osgr_1, location_northing_osgr_1, longitude_1, latitude_1, day_of_week,
                     first_road_class, results[2], second_road_class, light_conditions, weather_conditions,
                     road_surface_conditions, special_conditions_at_site, urban_or_rural_area, time_slot,
                     vehicle_type, sex_of_driver, age_band_of_driver, engine_capacity_cc, driver_home_area_type,
                     current_speed, current_travel_time, free_flow_travel_time]
    return start_columns


async def get_road(session, latitude, longitude):
    road_request = road_class_endpoint + 'key=' + urlparse.quote(tomtom_api_key) + '&point=' + urlparse.quote(
        str(latitude)) + ',' + urlparse.quote(str(longitude))

    async with session.get(road_request) as response:
        road = await response.json()
        return road['flowSegmentData']


async def get_speed_limit(session, latitude, longitude):
    speed_limit_request = speed_endpoint + 'points=' + urlparse.quote(str(latitude)) + ',' + urlparse.quote(
        str(longitude)) + '&IncludeSpeedLimit=true&speedUnit=KPH&travelMode=driving&key=' + urlparse.quote(
        bing_api_key)

    async with session.get(speed_limit_request) as response:
        speed_limit_data = await response.json()
        speed_limit = speed_limit_data['resourceSets'][0]['resources'][0]['snappedPoints'][0]['speedLimit']
        return speed_limit


# prediction main function
def show(request):
    start_time = time.time()
    global light_conditions, weather_conditions, road_surface_conditions, special_conditions_at_site, urban_or_rural_area, departure_time, time_slot, day_of_week, origin, destination, vehicle_type, sex_of_driver, age_band_of_driver, engine_capacity_cc, driver_home_area_type
    light_conditions = 1
    weather_conditions = 1
    road_surface_conditions = 1
    special_conditions_at_site = 0
    urban_or_rural_area = 1

    departure_time = datetime.datetime.now()
    time_slot = departure_time.hour
    day_of_week = int(departure_time.strftime("%w")) + 1

    obj_option = User_option.objects.last()
    origin = User_option._meta.get_field('origin').value_from_object(obj_option).replace(" ", "+")
    destination = User_option._meta.get_field('destination').value_from_object(obj_option).replace(" ", "+")

    obj = User_input.objects.last()
    vehicle_type = User_input._meta.get_field('vehicle_type').value_from_object(obj)
    sex_of_driver = User_input._meta.get_field('sex_of_driver').value_from_object(obj)
    age_band_of_driver = User_input._meta.get_field('age_band_of_driver').value_from_object(obj)
    engine_capacity_cc = User_input._meta.get_field('engine_capacity_cc').value_from_object(obj)
    driver_home_area_type = User_input._meta.get_field('driver_home_area_type').value_from_object(obj)

    async def main():
        async with aiohttp.ClientSession() as session:
            task = [asyncio.ensure_future(get_directions_data(session, origin, destination)),
                    asyncio.ensure_future(get_directions_data_1(session, origin, destination))]
            results = await asyncio.gather(*task)
        return results

    async def get_directions_data(session, origin, destination):
        nav_request = 'origin={}&destination={}&departure_time={}&key={}'.format(
            origin, destination,int(round(departure_time.timestamp())), google_api_key)
        dir_request = dir_endpoint + nav_request

        async with session.get(dir_request) as response:
            result_data = await response.json()
            return result_data

    async def get_directions_data_1(session, origin, destination):
        nav_request = 'origin={}&destination={}&departure_time={}&avoid={}&key={}'.format(
            origin, destination,int(round(departure_time.timestamp())),'tolls|highways', google_api_key)
        dir_request = dir_endpoint + nav_request

        async with session.get(dir_request) as response:
            result_data = await response.json()
            return result_data

    results = asyncio.run(main())
    directions = results[0]
    directions_1 = results[1]
    over_distance = directions['routes'][0]['legs'][0]['distance']['text']
    over_duration = directions['routes'][0]['legs'][0]['duration']['text']
    over_distance_1 = directions_1['routes'][0]['legs'][0]['distance']['text']
    over_duration_1 = directions_1['routes'][0]['legs'][0]['duration']['text']
    if over_distance == over_distance_1 and over_duration == over_duration_1:
        m, over_severity = asyncio.run(pred(directions))
        m_1 = 0
        over_severity_1 = 0
    else:
        m, over_severity = asyncio.run(pred(directions))
        m_1, over_severity_1 = asyncio.run(pred(directions_1))
        m_1 = m_1._repr_html_()
    # get html representation
    m = m._repr_html_()
    context = {
        'm': m,
        'm_1': m_1,
        'over_distance': over_distance,
        'over_duration': over_duration,
        'over_severity': over_severity,
        'over_distance_1': over_distance_1,
        'over_duration_1': over_duration_1,
        'over_severity_1': over_severity_1
    }
    logging.warning(time.time() - start_time)
    return render(request, 'show.html', context)
