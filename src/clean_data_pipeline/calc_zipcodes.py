from uszipcode import ZipcodeSearchEngine
search = ZipcodeSearchEngine()
import pandas as pd
import numpy as np


def _get_zips(df):
    """Method which calculates zipcodes for pairs of lats/longs

    Method uses the package uszipcode, a database scraped from the
    google maps api.

    Args:
        df(df): Dataframe containing lat/long pairs

    Returns:
           pickup_zips(list): List with pickup zipcodes
           dropoff_zips(list): List with dropoff zipcodes

    """
    p_lats = df.pickup_latitude.tolist()
    p_longs = df.pickup_longitude.tolist()
    d_lats = df.dropoff_latitude.tolist()
    d_longs = df.dropoff_longitude.tolist()

    pickup_zips = []
    dropoff_zips = []
    fails = []
    for i in range(len(p_lats)):
        p_lat = p_lats[i]
        p_long = p_longs[i]
        d_lat = d_lats[i]
        d_long = d_longs[i]
        
        try:
            pickup_zip = search.by_coordinate(p_lat, p_long, radius=10,
                                              returns=1)
            dropoff_zip = search.by_coordinate(d_lat, d_long, radius=10,
                                               returns=1)
            p_zip = int(pickup_zip[0]['Zipcode'])
            d_zip = int(dropoff_zip[0]['Zipcode'])
            pickup_zips.append(p_zip)
            dropoff_zips.append(d_zip)
            print(i)
        except IndexError:
            fails.append(i)
            
    df.drop(df.index[[fails]], inplace=True)
    df['pickup_zips'] = pickup_zips
    df['dropoff_zips'] = dropoff_zips
    
    return df


def filter_zips(df):
    """ Method to filter zips codes 
    
    """
    zips = pd.read_csv('data/zips_manhattan.csv')
    zips = np.unique(zips[['pickup_zips', 'dropoff_zips']])
    df = df.loc[df['pickup_zips'].isin(zips)]
    df = df.loc[df['dropoff_zips'].isin(zips)]
    return df

def clean_columns(data):
    trip_time_in_secs = ((data.trip_time_in_secs > 0.0) & (data.trip_time_in_secs <= 3600.0))
    trip_distance = ((data.trip_distance > 0.0) & (data.trip_distance <= 25.0))
    pickup_latitude = ((data.pickup_latitude >= 40.459518) & (data.pickup_latitude <= 41.175342))
    pickup_longitude = ((data.pickup_longitude >= -74.361107) & (data.pickup_longitude <= -71.903083))
    dropoff_latitude = ((data.dropoff_latitude >= 40.459518) & (data.dropoff_latitude <= 41.175342))
    dropoff_longitude = ((data.dropoff_longitude >= -74.361107) & (data.dropoff_longitude <= -71.903083))
    
    data = data[trip_time_in_secs & trip_distance & pickup_latitude & pickup_longitude
                & dropoff_latitude & dropoff_longitude]
        
    trip_time_in_secs = None
    trip_distance = None
    pickup_latitude = None
    pickup_longitude = None
    dropoff_latitude = None
    dropoff_longitude = None
    
    return data
  
