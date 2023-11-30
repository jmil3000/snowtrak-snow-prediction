import requests
import csv
import datetime
import os
import time
from dotenv import load_dotenv
import os

load_dotenv()

#API key
api_key = os.getenv('API_KEY')

#lat and lon (this will need to be updated to pull same lat and lon from user input)
lat = 40.58727
lon = -111.58180

def fetch_weather_data(unix_time):
    url = f'https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={unix_time}&appid={api_key}&units=imperial'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for time: {unix_time}")
        return None

def safe_fetch_weather_data(unix_time):
    #avoid fetching errors
    retries = 3
    while retries > 0:
        try:
            return fetch_weather_data(unix_time)
        except requests.exceptions.SSLError as e:
            print(f"SSL error encountered, retrying... ({retries} retries left)")
            time.sleep(5)
            retries -= 1
    print("Failed to fetch data after several retries.")
    return None

def fetch_elevation(lat, lon):
    url = f"https://api.opentopodata.org/v1/test-dataset?locations={lat},{lon}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data['results'][0]['elevation']
    else:
        print("Error fetching elevation data")
        return None

def get_unix_time(date):
    #time
    unix_time = int(time.mktime(date.timetuple()))
    return unix_time

file_path = '7_data.csv'
file_exists = os.path.isfile(file_path)

with open(file_path, mode='a', newline='') as file:
    #this will need to be changed as well, right now the file has to not exist for this part to work
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow(['Unix Time', 'Clouds', 'Dew Point', 'Feels Like', 'Humidity', 'Pressure', 'Snowfall', 'Temp', 'Visibility', 'Wind Speed', 'Elevation'])
    today = datetime.datetime.now()
    for i in range(7, 0, -1):
        day = today - datetime.timedelta(days=i)
        unix_time = get_unix_time(day)
        weather_data = safe_fetch_weather_data(unix_time)
        if weather_data and 'data' in weather_data and weather_data['data']:
            hourly_data = weather_data['data'][0]  # Extract the first data entry
            clouds = hourly_data.get('clouds', 0)
            dew_point = hourly_data.get('dew_point', 0)
            feels_like = hourly_data.get('feels_like', 0)
            humidity = hourly_data.get('humidity', 0)
            pressure = hourly_data.get('pressure', 0)
            snowfall = hourly_data.get('snow', {}).get('1h', 0)
            temp = hourly_data.get('temp', 0)
            visibility = hourly_data.get('visibility', 0)
            wind_speed = hourly_data.get('wind_speed', 0)
            elevation = fetch_elevation(lat, lon)
            writer.writerow([unix_time, clouds, dew_point, feels_like, humidity, pressure, snowfall, temp, visibility, wind_speed, elevation])