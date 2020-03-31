# Expands the wait data by 1) interpolating the wait time for hours without
# tweets, and 2) expands the date features

# import necessary packages
import pandas as pd
import datetime
from datetime import datetime, time, timedelta


def interpolate_wait(df, hours):
    """ Interpolates the wait time for hours without tweets by resampling the
    time to hourly, forward-filling the wait time (since the wait is in effect
    until an update tweet), and removing non-sailing hours.

    Args:
        df: data frame with 'time' column and 'wait time' column
        hours: tuple of strings with start and end hours for service (use 24hr 
            clock). eg. ('5', '23') for 5 am to 11 pm service

    Returns:
        df - expanded df with any extra columns retained
    """
    # make a copy of the df
    df = df.copy()

    # set time as index
    df = df.set_index('time')

    # convert to US/Pacific time zone
    df = df.tz_convert('US/Pacific')

    # get start and end times
    start = datetime.combine(df.index.min().date(), 
                                      time(int(hours[0]), 0))
    end = datetime.combine(df.index.max().date() + timedelta(days=1), 
                                    time(int(hours[1]), 0))
    
    # create list of dates
    sod = pd.date_range(start, end, freq='D', tz='US/Pacific')

    # create dataframe with each start of day, no wait
    sod_df = pd.DataFrame(sod)
    sod_df.columns = ['time']
    sod_df = sod_df.set_index('time')
    sod_df['wait_time'] = 0

    # append start of day dataframe to df
    df = df.append(sod_df)

    # resample times to hour intervals, adding the "missing" hours, 
    # and filling the wait time forward
    df = df.resample('1H').ffill()

    # remove non-sailing times
    df = df.between_time(hours[0]+":00", hours[1]+":00")

    return df


def expand_date(df):
    """Adds columns with year, month, day, hour, day of year, week, weekday.

    Args:
        dataframe w/ datetime index
    
    Returns:
        copy of dataframe with columns added
    """
    df = df.copy()
    df['year'] = df.index.year
    df['month'] = df.index.month
    df['day'] = df.index.day
    df['hour'] = df.index.hour
    df['dayofyear'] = df.index.dayofyear
    df['week'] = df.index.week
    df['weekday'] = df.index.weekday
    return df


def main():
    """Expands the wait data by 1) interpolating the wait time for hours 
    without tweets, and 2) expands the date features  
    """

    # import data
    ed_df = pd.read_csv('../data/hour_extracted/edmonds.csv')
    ki_df = pd.read_csv('../data/hour_extracted/kingston.csv')

    # convert to datetime
    ed_df['time'] = pd.to_datetime(ed_df['time'], utc=True)
    ki_df['time'] = pd.to_datetime(ki_df['time'], utc=True)

    # interpolate wait for each hour
    ed_df = interpolate_wait(ed_df, ('5', '1'))
    ki_df = interpolate_wait(ki_df, ('4', '1'))

    # expand date features
    ed_df = expand_date(ed_df)
    ki_df = expand_date(ki_df)

    # save as csv
    ed_df.to_csv('../data/expanded/edmonds.csv', index=True)
    ki_df.to_csv('../data/expanded/kingston.csv', index=True)

if __name__ == "__main__":
    main()