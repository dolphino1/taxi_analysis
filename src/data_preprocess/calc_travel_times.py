import pandas as pd
import numpy as np
import random
from src.tools.tools import unpickle, subset_variables, map_to_period
from src.tools.tools import find_df_period
from src.tools.tools import haversine_distance

TIME_PERIODS = 6
DF_PATH = 'data/zips_manhattan.csv'
TRAVEL_DF_PATH = 'data/pickled_objects/travel_time_df.pkl'
AVERAGE_DF_PATH = 'data/pickled_objects/average_travel_time_df.pkl'


class CalculateTravelTimes(object):
    """Class which calculates average travel time between zones

    """

    def __init__(self, load_data=True, time_periods=TIME_PERIODS,
                 travel_df_path=TRAVEL_DF_PATH, df_path=DF_PATH,
                 average_df_path=AVERAGE_DF_PATH):

        if not load_data:
            self.df = pd.read_csv(df_path, skipinitialspace=True)
            self.df = self.df.sort_values(['pickup_zips', 'dropoff_zips'],
                                          ascending=[1, 1])

            self.df.dropoff_datetime = pd.to_datetime(self.df.
                                                      dropoff_datetime)
            self.df.pickup_datetime = pd.to_datetime(self.df.
                                                     pickup_datetime)

            self.df = subset_variables(self.df, ['pickup_zips', 'dropoff_zips',
                                                 'pickup_datetime',
                                                 'dropoff_datetime',
                                                 'trip_time_in_secs',
                                                 'pickup_longitude',
                                                 'pickup_latitude',
                                                 'dropoff_longitude',
                                                 'dropoff_latitude'])

            self.zips = np.unique(self.df[['pickup_zips', 'dropoff_zips']])

        else:
            self.travel_df = unpickle(travel_df_path)
            self.average_travel_df = unpickle(average_df_path)

    def _calc_travel_time(self, df, pickle_path, time_period, num_of_samples):
        """Method which calculates average travel-time between zones for hour
           of the day.

        Method calculates travel time by going through each pair of pickup
        and dropoff zips and getting mean travel time between each zone for
        each time_period.

        Args:
            df(df): dataframe containing the trip time in secs

        Returns:
                travel_df(df): dataframe containing traveltime in minutes
        """
        subset_df = df.copy()
        df = find_df_period(subset_df, 'pickup_datetime', time_period)
        p_zips = []
        d_zips = []
        time_periods = []
        mean_travel_times = []
        pickup_zips = np.unique(df['pickup_zips'])
        dropoff_zips = np.unique(df['dropoff_zips'])
        zip_pairs = self.get_tuples(df)
        for period in range(0, time_period):
            for zips in zip_pairs:
                p_zip = zips[0]
                d_zip = zips[1]

                # Combinations with an observed trip for that period
                if p_zip in pickup_zips and d_zip in dropoff_zips:
                    full_df = df[(df['pickup_zips'] == p_zip) &
                                 (df['dropoff_zips'] == d_zip) &
                                 (df['time_period'] == period)]

                    # If no trips made in that period, use observed mean
                    if not full_df.empty:
                        travel_time = np.mean(full_df['trip_time_in_secs'])
                        travel_time = travel_time / 60
                        travel_time = randomize_travel_time(travel_time, 0.5)

                    else:
                        zip_df = df[(df['pickup_zips'] == p_zip) &
                                    (df['dropoff_zips'] == d_zip)]

                        if not zip_df.empty:
                            travel_time = np.mean(zip_df['trip_time_in_secs'])
                            travel_time = travel_time / 60
                            travel_time = randomize_travel_time(travel_time,
                                                                0.5)
                        else:
                            pickup_df = df[(df['pickup_zips'] == p_zip)]
                            dropoff_df = df[(df['dropoff_zips'] == d_zip)]
                            travel_time = get_travel_time(pickup_df,
                                                          dropoff_df,
                                                          num_of_samples,
                                                          'no_pair')
                            travel_time = np.mean(travel_time)
                            travel_time = randomize_travel_time(travel_time,
                                                                0.5)

                # No pickup observed in zone, use travel-time method
                elif p_zip not in pickup_zips and d_zip in dropoff_zips:
                    dropoff_df = df[(df['dropoff_zips'] == p_zip)]
                    fake_df = df[(df['dropoff_zips'] == d_zip)]
                    travel_time = get_travel_time(dropoff_df, fake_df,
                                                  num_of_samples, 'no_pzip')
                    travel_time = np.mean(travel_time)
                    travel_time = randomize_travel_time(travel_time, 0.5)

                # No dropoff observed in zone, use travel-time method
                elif d_zip not in dropoff_zips and p_zip in pickup_zips:
                    pickup_df = df[(df['pickup_zips'] == p_zip)]
                    fake_df = df[(df['pickup_zips'] == d_zip)]
                    travel_time = get_travel_time(pickup_df, fake_df,
                                                  num_of_samples, 'no_dzip')
                    travel_time = np.mean(travel_time)
                    travel_time = randomize_travel_time(travel_time, 0.5)

                p_zips.append(p_zip)
                d_zips.append(d_zip)
                mean_travel_times.append(travel_time)
                time_periods.append(period)

        columns = ['pickup_zips', 'dropoff_zips', 'time_period',
                   'mean_travel_time']
        travel_df = pd.DataFrame(columns=columns)
        travel_df['pickup_zips'] = p_zips
        travel_df['dropoff_zips'] = d_zips
        travel_df['time_period'] = time_periods
        travel_df['mean_travel_time'] = mean_travel_times

        return travel_df

    def get_tuples(self, df):
        """Method which calculates the each possible combination of trips

        The method is used because it is more robust than itertools
        permutations. The method is called in _calc_travel_time method.

        Args:
            df(df): Containing all unique zipcodes

        Returns:
             zip_pairs(list): list of tuples containing all combos
        """
        unique_zips = np.unique(df[['pickup_zips', 'dropoff_zips']])
        zip_pairs = []

        for zip_1 in unique_zips:
            for zip_2 in unique_zips:
                pair = (zip_1, zip_2)
                zip_pairs.append(pair)

        return zip_pairs

    def simulate_travel_time(self, start_zip, end_zip, datetime):
        """Method given a start_zip, end_zip and datetime returns travel-time

        Method unpickle a preprocessed df, containing calculated traveltime
        An exception is raised if no observations are contained

        Args:
            start_zip(int): Trip starting zone
            dropoff_zip(int): Trip end point
            datetime(datetime): The datetime to find the period for

        Returns:
            travel_time(int): expected travel time from zone to zone at period
        """
        time_period = map_to_period(datetime, TIME_PERIODS)

        index = self.travel_df[(self.travel_df['pickup_zips'] == start_zip) &
                               (self.travel_df['dropoff_zips'] == end_zip) &
                               (self.travel_df['time_period'] == time_period)]

        travel_time = float(index['mean_travel_time'])
        return travel_time

    def return_travel_time_dict(self, pickup_zip, datetime):
        """Returns a dictionary of travel-time to each zone at time

        """
        travel_df = self.travel_df.copy()
        time_period = map_to_period(datetime, TIME_PERIODS)
        travel_df = travel_df[(travel_df['time_period'] == time_period)]
        travel_df = travel_df[(travel_df['pickup_zips'] == pickup_zip)]
        travel_df = travel_df[['dropoff_zips', 'mean_travel_time']]
        dct = travel_df.set_index('dropoff_zips').T.to_dict('records')[0]

        return dct

    @staticmethod
    def _get_mean_zip_time(df, pickle_path, time_periods):
        """Method which calculates average trip time for pickup zone

        Args:
            df(df): dataframe containing variables needed to calculate

        Returns:
            time_df(df): df containing average wait time for zones

        """
        p_zips = np.unique(df[['pickup_zips', 'dropoff_zips']])
        df = find_df_period(df, 'pickup_datetime', time_periods)
        trip_times = []
        pickup_zips = []
        time_period_lst = []

        for p_zip in p_zips:
            pickup_df = df[df['pickup_zips'] == p_zip].copy()
            for period in range(0, time_periods):
                period_df = pickup_df[pickup_df['pickup_zips'] == p_zip].copy()

                if not period_df.empty:
                    trip_time = np.mean(period_df['trip_time_in_secs'])
                else:
                    trip_time = 0

                time_period_lst.append(period)
                trip_times.append(trip_time)
                pickup_zips.append(p_zip)

        columns = ['pickup_zips', 'mean_zone_time']
        time_df = pd.DataFrame(columns=columns)
        time_df['pickup_zips'] = pickup_zips
        time_df['mean_zone_time'] = trip_times
        time_df['mean_zone_time'] = time_df['mean_zone_time'] / 60
        time_df['time_period'] = time_period_lst

        return time_df

    def return_average_travel_time(self, datetime):
        """Method which returns average trip time for each zip

        Args:
            start_zip(int): zipcode to return average travel-time for

        Returns:
              dct(dict): dictioanry containing average wait time for zones

        """
        time_period = map_to_period(datetime, TIME_PERIODS)
        df = self.average_travel_df
        df = df[df['time_period'] == time_period]
        dct = df.set_index('pickup_zips').T.to_dict('records')[0]

        return dct


def get_travel_time(pickup_df, dropoff_df, num_of_samples, case_type):
    """Method to get travel time between zip code centroids

    Method has a local variable average_speed which is the average speed
    of a medallion in manhattan in kilometres.

    Args:
        pickup_df(df): area where the pickup occured
        dropoff_df(df): area where the dropoff occured

    Returns:
        travel_time(float): travel_time between zips
    """
    average_speed = 13.6955174
    travel_times = []
    random.seed(2)
    for i in range(num_of_samples):
        length = min(len(pickup_df), len(dropoff_df))
        index = random.randint(0, length - 1)
        subset_pickup_df = pickup_df.iloc[index]
        subset_dropoff_df = dropoff_df.iloc[index]

        if case_type == 'no_pzip':
            lat_one = subset_pickup_df['dropoff_latitude']
            lon_one = subset_pickup_df['dropoff_longitude']
            lat_two = subset_dropoff_df['dropoff_latitude']
            lon_two = subset_dropoff_df['dropoff_longitude']

        elif case_type == 'no_dzip':
            lat_one = subset_pickup_df['pickup_latitude']
            lon_one = subset_pickup_df['pickup_longitude']
            lat_two = subset_dropoff_df['pickup_latitude']
            lon_two = subset_dropoff_df['pickup_longitude']

        elif case_type == 'no_pair':
            lat_one = subset_pickup_df['pickup_latitude']
            lon_one = subset_pickup_df['pickup_longitude']
            lat_two = subset_dropoff_df['dropoff_latitude']
            lon_two = subset_dropoff_df['dropoff_longitude']

        dist = haversine_distance(lat_one, lon_one, lat_two, lon_two)
        travel_time = dist / average_speed
        travel_time = travel_time * 60
        travel_times.append(travel_time)

    return travel_times


def randomize_travel_time(travel_time, random_cut_off):
    number_1 = np.random.uniform()
    number_2 = np.random.uniform(0, 0.6)

    if number_1 < random_cut_off:
        travel_time = travel_time - travel_time * number_2

    else:
        travel_time = travel_time - travel_time * number_2

    return travel_time
