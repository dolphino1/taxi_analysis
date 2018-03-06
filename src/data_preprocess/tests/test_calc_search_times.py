import unittest
from src.data_preprocess.calc_search_time import CalculateSearchTimes
import datetime as dt
import numpy as np
import pandas as pd
from src.tools.tools import find_df_period
TIME_PERIODS = 6
DF_PATH = 'src/data_preprocess/tests/calc_search_time_test_data/'
DF_PATH += 'calc_search_time_dummy_data.csv'
SEARCH_PATH = 'src/data_preprocess/tests/calc_search_time_test_data/'
SEARCH_PATH += 'calc_search_time_dummy_df.pkl'


class CalcSearchTimeTestCase(unittest.TestCase):

    def test_calc_search_time(self):
        """ Method to calculate wait times then use simulate search to see
            if they are looked up correctly. Tests if the number of observation
            is the expected amount. and if the sum of average is correct
        """

        obj = CalculateSearchTimes(False, TIME_PERIODS,
                                   search_path=SEARCH_PATH, df_path=DF_PATH)

        self.assertTrue(len(np.unique(obj.df['medallion'])) == 2)
        self.assertTrue(len(np.unique(obj.df['pickup_zips'])) == 8)

        time_periods = 6
        search_df = obj._calc_search_time(obj.df, SEARCH_PATH,
                                          obj.zips, 30, time_periods)

        self.assertTrue(len(search_df) == len(obj.zips) * time_periods)
        self.assertTrue(np.sum(search_df['observations']) == 3)

        self.assertTrue(np.max(search_df['average_wait']) ==
                        1666.6666666666667)

    def test_find_df_period(self):
        """Test if a df datetime column is correctly converted to time periods

        """
        test_search_df = pd.read_csv(DF_PATH)
        result_1 = find_df_period(test_search_df, 'pickup_datetime', 6)
        p_time_periods_1 = result_1['time_period'].tolist()
        p_intervals_1 = [2, 2, 2, 2, 2, 3, 3, 3, 4, 4, 4]

        result_2 = find_df_period(test_search_df, 'pickup_datetime', 4)
        p_time_periods_2 = result_2['time_period'].tolist()
        p_intervals_2 = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2]

        self.assertTrue(p_time_periods_1 == p_intervals_1)
        self.assertTrue(p_time_periods_2 == p_intervals_2)

    def test_simulate_search(self):
        """Test unpickling object and return a search time

        """
        obj = CalculateSearchTimes(True, TIME_PERIODS,
                                   search_path=SEARCH_PATH, df_path=DF_PATH)
        dt1 = dt.datetime(2017, 8, 9, 14, 56, 40, 796658)
        dt2 = dt.datetime(2017, 8, 9, 17, 56, 40, 796658)
        dt3 = dt.datetime(2017, 8, 9, 10, 56, 40, 796658)
        zip_1 = 10028
        zip_2 = 10027
        zip_3 = 10008
        result1 = obj.simulate_search(zip_3, dt1)
        self.assertTrue(result1 == 1666.6666666666667)

        result2 = obj.simulate_search(zip_1, dt2)
        self.assertTrue(result2 == 24.0)

        result3 = obj.simulate_search(zip_2, dt2)
        self.assertTrue(result3 == 1666.6666666666667)

        result4 = obj.simulate_search(zip_2, dt3)
        self.assertTrue(result4 == 11.0)

    def test_get_time_period_search(self):
        """ Test get time period search
        """
        obj = CalculateSearchTimes(True, TIME_PERIODS,
                                   search_path=SEARCH_PATH, df_path=DF_PATH)
        dt1 = dt.datetime(2017, 8, 9, 14, 56, 40, 796658)
        dt2 = dt.datetime(2017, 8, 9, 17, 56, 40, 796658)
        dt3 = dt.datetime(2017, 8, 9, 10, 56, 40, 796658)
        result1 = obj.get_time_period_search(dt1)
        result2 = obj.get_time_period_search(dt2)
        result3 = obj.get_time_period_search(dt3)

        self.assertTrue(np.mean(list(result1.values())) == 1666.6666666666667)
        self.assertTrue(np.mean(list(result2.values())) != 1666.6666666666667)
        self.assertTrue(np.mean(list(result3.values())) != 1666.6666666666667)


if __name__ == '__main__':
    unittest.main()
