import pandas as pd
import numpy as np
import pickle


def read_data(name):
    """Method to read in a csv and attach as an attribute

    Args:
        name(string): Name of file to be read in

    Return: df(dataframe): csv file converted to pandas dataframe

    """
    df = pd.read_csv(name, skipinitialspace=True)

    return df


def pickle_obj(obj, name):
    """Method which serialises a python object

    Method is useful for getting around the large file sizes

    Args:
        obj(object): Python object to be serialised
        name(string): Name of serialised object
    """
    pickle.dump(obj, open(name, "wb"))

    
def merge_dfs(df1, df2):
    df = pd.concat([df1, df2], axis=1)
    return df


def unpickle(name):
    """Method which unserialises a python object

    Method is useful for getting around the large file sizes

    Args:
        name(string): Name of serialised object

    Returns:
          obj(object): Python object to be unserialised
    """
    obj = pickle.load(open(name, "rb"))

    return obj


def extract_sample(df, n_rows):
    """Method extract a subsample of a df and attach as an attribute

    Args:
        df(df): dataframe to extract a sample from
        n_rows(int): The number of rows the new df will contain

    Returns:
           sample_df(df): dataframe containing sample
    """
    sample_df = df.loc[0:n_rows - 1]
    del df

    return sample_df


def subset_variables(df, variables):
    """ Method to subset a dataframe, containing only specified variables

    Args:
        df(df): dataframe containing the redundant variables
        variables(list of strings): varibales to remain in the df

    Returns:
           df(df): Df with subsetted variables
    """

    df = df[variables]

    return df

def get_variable_range(df, column_name, lower_bound, upper_bound):
    """Method which subsets the data within certain coordinates

    The method calls subset_location and returns a dataframe in a certain
    radius around the centre of manhattan.

    Args:
        df(dataframe): dataframe to be subsetted
        min_long(float): Lower bound for longitude
        max_long(float): Upper bound for longitude
        min_lat(float): Lower bound for latitude
        max_lat(float): Upper bound for latitude

    Returns:
           df(dataframe): subsetted dataframe

    """
    df = df[(df[column_name] >= lower_bound) &
            (df['pickup_latitude'] <= upper_bound)]
    
    return df


def draw_boundary(df, mile_radius):
    """Method which subsets df based on a defined radius around nyc centre

    The method calls subset_location and returns a dataframe in a certain
    radius around the centre of manhattan.

    Args:
        mile_radius(float): Radius to subset data around NYC Centre
        df(dataframe): With lats and longs to encircle

    Return:
          df(dataframe): subset df with lats and longs within a radius

    """
    nyc_lat = 40.719681
    nyc_lon = -74.00536
    max_lat = nyc_lat + mile_radius / 69
    min_lat = nyc_lat - mile_radius / 69
    max_long = nyc_lon + mile_radius / 52
    min_long = nyc_lon - mile_radius / 52
    df = subset_location(df, min_long, max_long, min_lat, max_lat)

    return df


def subset_location(df, min_long, max_long, min_lat, max_lat):
    """Method which subsets the data within certain coordinates

    The method calls subset_location and returns a dataframe in a certain
    radius around the centre of manhattan.

    Args:
        df(dataframe): dataframe to be subsetted
        min_long(float): Lower bound for longitude
        max_long(float): Upper bound for longitude
        min_lat(float): Lower bound for latitude
        max_lat(float): Upper bound for latitude

    Returns:
           df(dataframe): subsetted dataframe

    """
    df = df[(df['pickup_longitude'] >= min_long) &
            (df['pickup_longitude'] <= max_long) &
            (df['pickup_latitude'] >= min_lat) &
            (df['pickup_latitude'] <= max_lat)]
    return df


def map_to_period(datetime, time_periods):
    """
    Divides the day into n time_periods and returns the index of the
    the period the datetime falls into.

    Args:
        datetime: datetime to check
        time_periods: number of time periods to divide the day into

    Returns:
           index of time period: 0 -> time_periods - 1 (int)
        """
    decimal_hour = datetime.hour + (datetime.minute / 60)
    cut_offs = np.linspace(0, 24, time_periods + 1)
    return np.argmax(cut_offs >= decimal_hour) - 1


def find_df_period(df, column_name, time_periods):
    """
    Divides a df column to their respective time_period

    Args:
        df(df): df containing column to find the period for
        column_name(string): the datetime column to find time-periods for
        time_periods(int): number of time periods to divide the day into

    Returns:
        df(df): df containing new columns 'time_periods'
    """
    intervals = []
    df[column_name] = pd.to_datetime(df[column_name])
    datetimes = df[column_name].tolist()
    for datetime in datetimes:
        decimal_hour = datetime.hour + (datetime.minute / 60)
        cut_offs = np.linspace(0, 24, time_periods + 1)
        intervals.append(np.argmax(cut_offs >= decimal_hour) - 1)

    df['time_period'] = intervals
    return df


def haversine_distance(lat_one, lon_one, lat_two, lon_two):
    """
        Computes the haversine distances between two vectors in miles.

        If in the future we want to avoid using this function because of time
        constraints, we shoud preprocess the data to 3d coordinates and
        compute euclidean distance.

        Args:
            lat_one: numpy array first vectors lats
            one_one: numpy array first vectors lons
            lat_two: numpy array second vectors lats
            lon_two: numpy array second vectors lons

        Returns:
            vector of haversine distances in miles

    """
    lat_one = np.radians(lat_one)
    lon_one = np.radians(lon_one)
    lat_two = np.radians(lat_two)
    lon_two = np.radians(lon_two)

    distance_lat = lat_one - lat_two
    distance_lon = lon_one - lon_two

    a = (np.sin(distance_lat / 2) ** 2 +
         np.cos(lat_two) *
         np.cos(lat_one) *
         np.sin(distance_lon / 2)**2)
    c = 2 * np.arcsin(np.sqrt(a))

    return 6371 * c


def get_centroids(df, lat_column, lon_column):
        """
        This function takes in a dataframe, and returns the centroid of its
        pickup_latitude and pickup_longitude.

        Args:
            df: Pandas dataframe
            lat_column(str): latitude column name
            lon_column(str): longitude column name

        Returns:
               (sum_lat/n,sum_lon/n): tuple containing the centroid
        """
        points = np.array(df[[lat_column, lon_column]])
        n = points.shape[0]
        sum_lon = np.sum(points[:, 1])
        sum_lat = np.sum(points[:, 0])

        return (sum_lat / n, sum_lon / n)
