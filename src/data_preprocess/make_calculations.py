#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 11:47:17 2017

@author: d
"""
import os
import sys
sys.path.append(os.getcwd())
from src.data_preprocess.calc_travel_times import CalculateTravelTimes
from src.data_preprocess.calc_mean_fare import CalculateFare
from src.data_preprocess.calc_search_time import CalculateSearchTimes
from src.data_preprocess.transition import Transition
DF_PATH = 'data/zips_manhattan.csv'
TRAVEL_DF_PATH = 'data/pickled_objects/travel_time_df.pkl'
AVERAGE_DF_PATH = 'data/pickled_objects/average_travel_time_df.pkl'
SEARCH_PATH = 'data/pickled_objects/wait_df.pkl'
FARE_PATH = 'data/pickled_objects/average_fare_df.pkl'
CSV_PATH = 'data/zips_manhattan.csv'
ZIP_CODES_PATH = 'data/OrderedZipCodes.json'
PICKLE_PATH = 'data/trasition_matrices.pickle'
MAX_WAIT_TIME = 30
TIME_PERIODS = 6


def make_calculations():
    travel_time_obj = CalculateTravelTimes(load_data=False)
    travel_time_obj._calc_travel_time(travel_time_obj.df,
                                      pickle_path=TRAVEL_DF_PATH,
                                      time_period=TIME_PERIODS)

    travel_time_obj._get_mean_zip_time(travel_time_obj.df,
                                       pickle_path=AVERAGE_DF_PATH,
                                       time_periods=TIME_PERIODS)

    search_time_obj = CalculateSearchTimes(load_data=False)

    search_time_obj._calc_search_time(search_time_obj.df,
                                      pickle_path=SEARCH_PATH,
                                      zips=search_time_obj.zips,
                                      max_wait_time=MAX_WAIT_TIME,
                                      time_periods=TIME_PERIODS)

    calc_fare_obj = CalculateFare(load_data=False)
    calc_fare_obj._calc_average_zip_fare(calc_fare_obj.df,
                                         pickle_path=FARE_PATH,
                                         time_periods=TIME_PERIODS)
    Transition(load_data=False)


if __name__ == "__main__":
    make_calculations()
