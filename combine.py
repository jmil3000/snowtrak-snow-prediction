import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

def combine_weather_data(file_path_7_data, file_path_daily_weather_data):
    #csv to df
    df_7_data = pd.read_csv(file_path_7_data)
    df_daily_weather_data = pd.read_csv(file_path_daily_weather_data)
    required_columns = df_7_data.columns.tolist()
    df_converted_daily = pd.DataFrame(columns=required_columns)

    for index, row in df_daily_weather_data.iterrows():
        converted_row = {}
        converted_row['Unix Time'] = int(pd.Timestamp(row['dt']).timestamp())
        converted_row['Clouds'] = row.get('clouds', 0)
        converted_row['Dew Point'] = row.get('dew_point', 0)
        converted_row['Feels Like'] = row.get('feels_like_day', 0)
        converted_row['Humidity'] = row.get('humidity', 0)
        converted_row['Pressure'] = row.get('pressure', 0)
        converted_row['Snowfall'] = row.get('snow', 0) if pd.notna(row.get('snow')) else 0
        converted_row['Temp'] = row.get('Temperature (Day)', 0)
        converted_row['Visibility'] = row.get('visibility', 10000)
        converted_row['Wind Speed'] = row.get('wind_speed', 0)
        converted_row['Elevation'] = df_7_data['Elevation'].iloc[0]

        df_converted_daily = df_converted_daily.append(converted_row, ignore_index=True)

    combined_df = pd.concat([df_7_data, df_converted_daily], ignore_index=True)
    return combined_df

file_path_7_data = os.getenv('7_DATA_PATH')  # past 7 days csv
file_path_daily_weather_data = os.getenv('DWD_PATH')  # next 8 days csv

combined_df = combine_weather_data(file_path_7_data, file_path_daily_weather_data)

#combine
combined_csv_path = os.getenv('COMBINE_PATH')  #save combo file
combined_df.to_csv(combined_csv_path, index=False)
