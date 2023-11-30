import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from dotenv import load_dotenv
import os

load_dotenv()

def preprocess_data(df):
    #unix to dt
    df['Date'] = pd.to_datetime(df['Unix Time'], unit='s')
    #seasons
    def get_season(month):
        if 3 <= month <= 5:
            return 'spring'
        elif 6 <= month <= 8:
            return 'summer'
        elif 9 <= month <= 11:
            return 'autumn'
        else:
            return 'winter'
    df['Season'] = df['Date'].dt.month.apply(get_season)
    #hot one encoding
    season_dummies = pd.get_dummies(df['Season'], prefix='Season')
    df = pd.concat([df, season_dummies], axis=1)
    return df

def create_sequences(data, sequence_length=7):
    #sequence of 7 days
    sequences = []
    for i in range(len(data) - sequence_length):
        seq = data.iloc[i:i + sequence_length][['Temp', 'Humidity', 'Pressure', 'Snowfall', 'Visibility', 'Wind Speed', 'Dew Point', 'Elevation']]
        sequences.append(seq.values)
    return np.array(sequences)

combo_data_path = os.getenv('COMBINE_PATH')  #incoming data
combo_data = pd.read_csv(combo_data_path)
combo_processed = preprocess_data(combo_data)

scaler_path = os.getenv('SCALER_PATH')  #incoming scaler
scaler = joblib.load(scaler_path)

#normalize
features_to_normalize = ['Temp', 'Humidity', 'Pressure', 'Snowfall', 'Visibility', 'Wind Speed', 'Dew Point', 'Elevation']
combo_processed[features_to_normalize] = scaler.transform(combo_processed[features_to_normalize])
combo_sequences = create_sequences(combo_processed)

model_path = os.getenv('MODEL_PATH')  #incoming model
model = load_model(model_path, compile=False)
model.compile(optimizer='adam', loss='mean_squared_error')

predictions = model.predict(combo_sequences)
dummy_data = np.zeros((len(predictions), len(features_to_normalize)))
dummy_data[:, features_to_normalize.index('Snowfall')] = predictions.ravel()
inverse_predictions = scaler.inverse_transform(dummy_data)[:, features_to_normalize.index('Snowfall')]

import datetime
today = datetime.date.today()
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
snowfall_threshold = 0.5
significant_snowfall_predicted = False
for i, prediction in enumerate(inverse_predictions):
    prediction_date = today + datetime.timedelta(days=i)
    day_of_week = days_of_week[prediction_date.weekday()]
    if prediction > snowfall_threshold:
        significant_snowfall_predicted = True
    print(f"{day_of_week}: {prediction}")
if significant_snowfall_predicted:
    print("Looks like some powder is headed your way!")