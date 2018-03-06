#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 11:12:49 2017
@author: d
"""
import pandas as pd
import numpy as np
from src.tools.tools import unpickle, subset_variables, map_to_period
from src.tools.tools import find_df_period, pickle_obj

TIME_PERIODS = 6
DF_PATH = 'data/zips_manhattan.csv'
SEARCH_PATH = 'data/pickled_objects/wait_df.pkl'


class CalculateSearchTimes(object):
    """Class which calculates average waittimes for each zone.

    """

    def __init__(self, load_data=True, time_periods=TIME_PERIODS,
                 search_path=SEARCH_PATH, df_path=DF_PATH):

        if not load_data:
            self.df = pd.read_csv(df_path, skipinitialspace=True)
            self.df = subset_variables(self.df, ['medallion', 'pickup_zips',
                                                 'dropoff_zips',
                                                 'pickup_datetime',
                                                 'dropoff_datetime'])

            self.zips = np.unique(self.df[['pickup_zips', 'dropoff_zips']])
            self.df.dropoff_datetime = pd.to_datetime(self.df.dropoff_datetime)
            self.df.pickup_datetime = pd.to_datetime(self.df.pickup_datetime)
            self.path = search_path

        else:
            self.search_df = unpickle(search_path)

    @staticmethod
    def _calc_search_time(df, pickle_path, zips, max_wait_time, time_periods):
        """Method which calculates average wait-time for each zipcode

        Method calculates waittime, by grouping by medallion number and
        finding instances where drivers dropped someone off and had their next
        pickup in the same zone.

        Args:
            df(df): Dataframe to calculate wait times for
            zips(list): list of ints containing unique zips
            max_wait_time(int): maximum time between dropoff and next pickup

        Returns:
                wait_df(df): dataframe with waittime in minutes
        """
        max_wait_time = 60 * max_wait_time

        # Set up dataframe for wait times, and variables needed to calc them
        period_lst = list(range(0, time_periods))
        final_df_length = len(period_lst) * len(zips)

        wait_df = pd.DataFrame({'zips': np.tile(zips, len(period_lst)),
                                'time_period': np.repeat(period_lst,
                                                         len(zips)),
                                'total_wait': np.zeros(final_df_length),
                                'observations': np.zeros(final_df_length)})

        subset_df = df.copy()
        unique_medallions = np.unique(subset_df['medallion'])

        # For each driver shift df, so dropoff followed by pickup is found.
        for medallion in unique_medallions:
            med_df = subset_df.copy()
            med_df = subset_df[subset_df['medallion'] == medallion]
            med_df = med_df.sort_values(by='pickup_datetime')
            med_df.dropoff_zips = med_df.dropoff_zips.shift(1)
            med_df['backtime'] = med_df.dropoff_datetime.shift(1)
            med_df['backtime'] = pd.to_datetime(med_df['backtime'])
            med_df = med_df.fillna(0)
            med_df['diff'] = med_df.pickup_datetime - med_df.backtime
            med_df['diff'] = med_df['diff'].dt.total_seconds()
            med_df = med_df[(med_df['pickup_zips'] == med_df['dropoff_zips'])]
            med_df = med_df[(med_df['diff'] <= max_wait_time)]
            med_df = find_df_period(med_df, 'pickup_datetime', time_periods)
            unique_zips = np.unique(med_df['pickup_zips'])

            # For each dropoff/pickup find zone count, and total wait
            for zips in unique_zips:
                zip_df = med_df[med_df['pickup_zips'] == zips]
                unique_periods = np.unique(zip_df['time_period'])

            # For each time-period add the total wait and the observations
                for period in unique_periods:
                    period_df = zip_df[zip_df['time_period'] == period]
                    total_sum = zip_df['diff'].sum()
                    obs = len(period_df)
                    index = wait_df.loc[(wait_df['zips'] == zips) &
                                        (wait_df['time_period'] == period)]
                    row_to_update = index.index
                    total_wait_sum = index['total_wait'] + total_sum
                    total_obs = index['observations'] + obs
                    wait_df.loc[row_to_update, 'total_wait'] = total_wait_sum
                    wait_df.loc[row_to_update, 'observations'] = total_obs

        # Avoid division by zero if there are no obs, replace NaN with zero
        if wait_df['observations'].any() == 0:
            wait_df['average_wait'] = 0
        else:
            wait_df['average_wait'] = (wait_df['total_wait'] /
                                       wait_df['observations'])
        wait_df = wait_df.fillna(100000)
        wait_df['average_wait'] = wait_df['average_wait'] / 60

        return wait_df

    def simulate_search(self, pickup_zip, datetime):
        """Method given a pickup_zip and datetime returns an average search

        Method unpickle a preprocessed df, containing calculated waittimes

        Args:
            pickup_zip(int): Pickup Zipcode to find average waittime for
            datetime(datetime): The datetime to find the period for
        """
        df = self.search_df
        time_period = map_to_period(datetime, TIME_PERIODS)
        index = df.loc[(df['zips'] == pickup_zip) &
                       (df['time_period'] == time_period)]

        wait_time = float(index['average_wait'])
        return wait_time

    def get_time_period_search(self, datetime):
        """Method given a datetime returns a average searchtime


        Method unpickle a preprocessed df, containing calculated waittimes

        Args:
            datetime(datetime): The datetime to find the period for
        """

        df = self.search_df
        time_period = map_to_period(datetime, TIME_PERIODS)
        df = df[(df['time_period'] == time_period)]
        df = df[['zips', 'average_wait']]
        dct = df.set_index('zips').T.to_dict('records')[0]
        return dct

    def stocastic_search(self, pickup_zip, datetime):
        """
            Simulate a search time stocastically using an exponential
            distribution.

            Args:
                pickup_zip: zip code search time is calculated for
                datetime: dateti

            Returns:
                simulated search time based on exponential distribution in
                minutes.
        """
        df = self.search_df
        time_period = map_to_period(datetime, TIME_PERIODS)
        index = df.loc[(df['zips'] == pickup_zip) &
                       (df['time_period'] == time_period)]

        wait_time = int(index['average_wait'])
        wait_time = np.random.exponential(wait_time * (2 / 3))
        return wait_time
