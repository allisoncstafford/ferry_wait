# load necessary modules
import pandas as pd
from datetime import datetime, timedelta, date
import requests
import json
from pymongo import MongoClient
from typing import List
import pandas as pd
import numpy as np

# secret file location
secret_loc = "/Users/allisonhonold/.secrets/dark_sky_api.json"

# start and end dates
start_date = "2016-12-17"
end_date = "2020-01-01"

# location of interest
lat_long = (47.811784, -122.383250) # Edmonds ferry terminal (google)

def main():
    """Gets the Edmonds, WA, weather data from dark sky API and dumps it into
    the weather collection within the walk MongoDB.

    Based on Cristian Nuno's soccer_stats/Weather_Getter and export_weather
    https://github.com/cenuno/soccer_stats/blob/master/python/export_weather.py
    https://github.com/cenuno/soccer_stats/blob/master/python/weathergetter.py
    """
    # convert dates to datetime
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    
    # get list of dates in data range
    dates = get_dates_list(start_dt, end_dt)

    # load secret key
    with open(secret_loc, "r") as f:
        key = json.load(f)["key"]

    # store exclusions
    excl = "?exclude=currently,minutely,hourly,alerts,flags"

    # instatntiate MongoDB client
    client = MongoClient()
    db = client["ferry"]
    weather = db["weather"]

    # set api url
    dk_sky_url = 'https://api.darksky.net/forecast/'

    # Broken into sets in order to stay in the free use level of 
    # darksky weather api.

    # get_weather for first date - done
    # date = dates[0]
    # get_weather(date, lat_long[0], lat_long[1], key,
    #             dk_sky_url, excl, weather)

    # get_weather for next 998 dates
    # for date in dates[1:999]:
    #     get_weather(date, lat_long[0], lat_long[1], key,
    #                 dk_sky_url, excl, weather)

    # get_weather for next 1000 dates
    for date in dates[999:1999]:
        get_weather(date, lat_long[0], lat_long[1], key,
                    dk_sky_url, excl, weather)


def get_dates_list(initial_date: datetime, 
                   final_date: datetime) -> List[datetime]:
    """Create a list of datetime objects with each date between the initial_date
    and final_date.

    Args: 
        initial_date: the first date in the list
        final_data: the last date in the list
    
    Returns:
        a list of datetime objects with a one day interval between the initial
        and final dates.
    """
    return [initial_date + timedelta(x) 
            for x in range(int((final_date - initial_date).days)+8)]


def get_weather(date: datetime, lat, long, secret_key,
                base_url='https://api.darksky.net/forecast/', 
                exclusions="?exclude=currently,minutely,hourly,alerts,flags", 
                collection=None):
    """Retrieve weather for a particular date based on exclusions passed.
    Stores weather in mongoDB collection passed
    
    Args:
        date: datetime object
        lat: latitude of interest
        long: longitude of interest
        base_url: the base url of the weather api (default: darksky)
        exclusions: list of exclusions to pass to the api
        secret_key: your secret key to access the weather api
        collection: the MongoDB collection you would like to store the weather
            data in

    Returns:
        If no MongoDB collection, returns weather json.
        Else, data is stored in the collection passed.
    """
    date_str = date.strftime('%Y-%m-%d') + 'T12:00:00'
    url = f"{base_url}{secret_key}/{lat},{long},{date_str}{exclusions}"
    response = requests.get(url)
    output = response.json()
    output['date'] = date
    if collection == None:
        return output
    collection.insert_one(output)


def prep_weather(weather_data_json, today):
    """prepares weather data for modeling. Current model requires only 
    'ap_t_high100'.
    
    Args:
        weather_df: pandas dataframe of daily weather data json returned by 
            darksky api ex. pd.DataFrame(dk_sky_weather_json['daily']['data'])
        date: datetime of date
        
    Returns: single line weather dataframe only missing lats/longs for model 
        pipeline
    """
    weather_df = pd.DataFrame(np.zeros((1,10)), 
                            columns=['apparentTemperatureHigh',
                               'precipAccumulation'])
    for col in weather_df.columns:
        if col in weather_data_json.keys():
            weather_df[col] = weather_data_json[col]
    return weather_df


if __name__ == '__main__':
    main()