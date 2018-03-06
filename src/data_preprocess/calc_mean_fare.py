#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 09:59:09 2017

@author: d
"""

import pandas as pd
import numpy as np
from src.tools.tools import unpickle, map_to_period, find_df_period, pickle_obj

TIME_PERIODS = 6
DF_PATH = 'data/zips_manhattan.csv'
FARE_PATH = 'data/pickled_objects/average_fare_df.pkl'


class CalculateFare(object):
    """Class which calculates mean travel fare for each unique zone

    """

    def __init__(self, load_data=True, time_periods=TIME_PERIODS,
                 df_path=DF_PATH, fare_path=FARE_PATH):

        if not load_data:
            self.df = pd.read_csv(df_path, skipinitialspace=True)
            self.df = self.df.sort_values(['pickup_zips', 'dropoff_zips'],
                                          ascending=[1, 1])

            self.df.dropoff_datetime = pd.to_datetime(self.df.dropoff_datetime)
            self.df.pickup_datetime = pd.to_datetime(self.df.pickup_datetime)
            self.time_periods = time_periods

        else:
            self.fare_df = unpickle(fare_path)

    @staticmethod
    def _calc_average_zip_fare(df, pickle_path, time_periods):
        """Method which calculates average fare for pickup zone

        Args:
            df(df): dataframe containing variables needed to calculate the fare

        Returns:
            average_fare_df(df): df containing average fare for each zone

        """
        p_zips = np.unique(df[['pickup_zips', 'dropoff_zips']])
        df = find_df_period(df, 'pickup_datetime', time_periods)
        fare_amounts = []
        pickup_zips = []
        time_period_lst = []

        for zips in p_zips:
            pickup_df = df[df['pickup_zips'] == zips].copy()
            for period in range(0, time_periods):
                period_df = pickup_df[pickup_df['time_period'] == period]

                if not period_df.empty:
                    fare_amount = np.mean(period_df['fare_amount'])
                else:
                    fare_amount = 0

                fare_amounts.append(fare_amount)
                pickup_zips.append(zips)
                time_period_lst.append(period)

        columns = ['pickup_zips', 'mean_zone_fare', 'time_period']
        fare_df = pd.DataFrame(columns=columns)
        fare_df['pickup_zips'] = pickup_zips
        fare_df['mean_zone_fare'] = fare_amounts
        fare_df['time_period'] = time_period_lst

        return fare_df

    def return_average_fare(self, datetime):
        """Method which returns average trip time for one zipcode

        Args:
            start_zip(int): zipcode to return average travel-time for

        Returns:
            mean_travel_time(int): df containing average wait time for zones

        """
        df = self.fare_df
        time_period = map_to_period(datetime, TIME_PERIODS)
        df = df[df['time_period'] == time_period]
        dct = df.set_index('pickup_zips').T.to_dict('records')[0]

        return dct
