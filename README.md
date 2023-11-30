***SNOWTRAK***

Snowtrak is a snow and pow prediction application that pulls in current data and runs it through a LSTM model that has been trained on Brighton Ski Resort, specifically my favorite run, Wrens Hollow. For that reason Snowtrak currently is meant to be used for Brighton Ski Resort although support for more locations is planned. Make sure to set up your correct OpenWeatherAPI key and file paths in the .env_format file. The used coordinates can be found in the main.py file for easy access when running the application. Entire application is run by running the main.py file.

The model is currently a little iffy, occasionally giving negative snow values for example. Until fixed those days can be considered low or no snow at all.

All this code is 100% original, including the LSTM model and even the dataset. I built the dataset myself (currently small but growing, thus the iffy LSTM model), and trained the model on that data set using TensorFlow and Keras. The dataset went through different preprocessing techniques (inlcluding Standard Scaler, see .pkl file) and sequencing for the LSTM of course.