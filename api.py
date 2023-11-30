import requests
import pprint
import pytz
import pandas as pd
from pandas import json_normalize
import time
from dotenv import load_dotenv
import os

load_dotenv()

#API key
api_key = os.getenv('API_KEY')

def get_location_data(choice):
    if choice == '1':
        city = input("Enter the city name: ")
        state_code = input("Enter the state code: ")
        country_code = input("Enter the country code: ")
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{state_code},{country_code}&limit=1&appid={api_key}"
    elif choice == '2':
        zip_code = input("Enter the zip code: ")
        country_code = input("Enter the country code: ")
        url = f"http://api.openweathermap.org/geo/1.0/zip?zip={zip_code},{country_code}&appid={api_key}"
    else:
        lat = input("Enter latitude: ")
        lon = input("Enter longitude: ")
        return lat, lon
    response = requests.get(url)
    data = response.json()
    return data[0]['lat'], data[0]['lon']

def get_elevation(latitude, longitude):
    url = f"https://api.opentopodata.org/v1/test-dataset?locations={latitude},{longitude}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        elevation = data['results'][0]['elevation']
        return elevation
    else:
        return None
    
def get_historical_data(lat, lon, days=7):
    historical_data = []
    for day in range(days, 0, -1):
        # Unix timestamp for 'day' days ago
        unix_time = int(time.time()) - day * 86400
        # API Call for historical data
        url = f'https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={unix_time}&appid={api_key}&units=imperial'
        response = requests.get(url)
        data = response.json()
        # Extract daily data
        if 'current' in data:
            historical_data.append(data['current'])
    return historical_data

#begin user input
print("Welcome to Snowtrak! Would you like to:")
print("1. Search for report by location name")
print("2. Search for report by zip")
print("3. Search for report by exact coordinates")
choice = input("How would you like to search for the weather report? (1/2/3): ")

lat, lon = get_location_data(choice)
elevation = get_elevation(lat, lon)
if elevation is not None:
    print(f"Elevation for the provided coordinates: {elevation} meters")


historical_weather_data = get_historical_data(lat, lon)
df_historical = json_normalize(historical_weather_data, sep='_')
url = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly&appid={api_key}&units=imperial'
response = requests.get(url)
data = response.json()

daily_data = data.get('daily', [])
if daily_data:
    df_daily = json_normalize(daily_data, sep='_')
    #unix to dt
    df_daily['dt'] = pd.to_datetime(df_daily['dt'], unit='s')
    df_daily['sunrise'] = pd.to_datetime(df_daily['sunrise'], unit='s')
    df_daily['sunset'] = pd.to_datetime(df_daily['sunset'], unit='s')
    df_daily['moonrise'] = pd.to_datetime(df_daily['moonrise'], unit='s')
    df_daily['moonset'] = pd.to_datetime(df_daily['moonset'], unit='s')
    #dt to local time
    local_tz = pytz.timezone('America/Denver')
    def utc_to_local(utc_dt):
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        return local_tz.normalize(local_dt)
    df_daily['sunrise'] = df_daily['sunrise'].apply(utc_to_local)
    df_daily['sunset'] = df_daily['sunset'].apply(utc_to_local)
    df_daily['moonrise'] = df_daily['moonrise'].apply(utc_to_local)
    df_daily['moonset'] = df_daily['moonset'].apply(utc_to_local)
    #rename columns
    df_daily.rename(columns={'temp_day': 'Temperature (Day)', 'temp_min': 'Temperature (Min)', 'temp_max': 'Temperature (Max)'}, inplace=True)
    df_daily.to_csv('daily_weather_data.csv', index=False)

#historical+daily
combined_df = pd.concat([df_historical, df_daily], ignore_index=True)
combined_df.to_csv('daily_weather_data.csv', index=False)

alerts_data = data.get('alerts', [])
if alerts_data:
    df_alerts = json_normalize(alerts_data, sep='_')
    #unix to dt
    df_alerts['start'] = pd.to_datetime(df_alerts['start'], unit='s')
    df_alerts['end'] = pd.to_datetime(df_alerts['end'], unit='s')
    #dt to local time
    def utc_to_local(utc_dt):
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        return local_tz.normalize(local_dt)
    df_alerts['start'] = df_alerts['start'].apply(utc_to_local)
    df_alerts['end'] = df_alerts['end'].apply(utc_to_local)
    #rename columns
    df_alerts.rename(columns={'sender_name': 'Sender', 'event': 'Event', 'description': 'Description'}, inplace=True)
    df_alerts.to_csv('alerts_weather_data.csv', index=False)

#pprint.pprint(data)
