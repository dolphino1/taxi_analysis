import unittest
from src.data_preprocess.calc_travel_times import CalculateTravelTimes
import datetime as dt
import numpy as np

TIME_PERIODS = 6
NUM_SAMPLES = 4
DF_PATH = 'src/data_preprocess/tests/calc_travel_time_test_data/'
DF_PATH += 'calc_travel_time_dummy_data.csv'
TRAVEL_DF_PATH = 'src/data_preprocess/tests/calc_travel_time_test_data/'
TRAVEL_DF_PATH += 'test_travel_time_df.pkl'
AVERAGE_DF_PATH = 'src/data_preprocess/tests/calc_travel_time_test_data/'
AVERAGE_DF_PATH += 'test_average_travel_time_df.pkl'


class CalcTravelTimeTestCase(unittest.TestCase):

    def test__calc_travel_time(self):
        """ Method to calculate travel times then use simulate search to see
            if they are looked up correctly.
        """

        obj = CalculateTravelTimes(False, TIME_PERIODS,
                                   df_path=DF_PATH)

        travel_df = obj._calc_travel_time(obj.df, TRAVEL_DF_PATH, TIME_PERIODS,
                                          num_of_samples=NUM_SAMPLES)
        
        unique_zips = len(np.unique(travel_df[['pickup_zips',
                                               'dropoff_zips']]))

        self.assertTrue(len(travel_df) == unique_zips * unique_zips *
                        TIME_PERIODS)
    
    def test_simulate_travel_time(self):
        """ Method to test simulate search
        """

        obj = CalculateTravelTimes(TIME_PERIODS,
                                   travel_df_path=TRAVEL_DF_PATH)

        dt1 = dt.datetime(2017, 8, 9, 1, 56, 40, 796658)
        dt2 = dt.datetime(2017, 8, 9, 3, 56, 40, 796658)
        dt3 = dt.datetime(2017, 8, 9, 23, 56, 40, 796658)
        zip_1 = 10030
        zip_2 = 10027
        zip_3 = 10026
        zip_4 = 10031

        result1 = obj.simulate_travel_time(zip_2, zip_3, dt1)
        self.assertTrue(result1 == 0.5410414146292752)

        result2 = obj.simulate_travel_time(zip_2, zip_3, dt3)
        self.assertTrue(result2 ==  0.4792001275307506)

        result3 = obj.simulate_travel_time(zip_1, zip_4, dt2)
        self.assertTrue(result3 == 2.1717798852931)

    def test_return_travel_time_dict(self):
        """Method to test if travel_time dict is looked up correctly
        """

        obj = CalculateTravelTimes(TIME_PERIODS,
                                   travel_df_path=TRAVEL_DF_PATH)

        dt1 = dt.datetime(2017, 8, 9, 14, 56, 40, 796658)
        dt2 = dt.datetime(2017, 8, 9, 18, 56, 40, 796658)
        dt3 = dt.datetime(2017, 8, 9, 23, 56, 40, 796658)
        zip_1 = 10028
        zip_2 = 10027

        dct1 = obj.return_travel_time_dict(zip_1, dt1)
        self.assertTrue(dct1[10028] == 0)

        dct2 = obj.return_travel_time_dict(zip_2, dt3)
        self.assertTrue(dct2[10026] == 0.47920012753075059)

    def test_get_tuples(self):
        """Test getting all possible combos of zips
        """

        obj = CalculateTravelTimes(False, TIME_PERIODS,
                                   df_path=DF_PATH)

        len_unique_zips = len(np.unique(obj.df[['pickup_zips',
                                                'dropoff_zips']]))
        tuples = obj.get_tuples(obj.df)
        self.assertTrue(len(tuples) == len_unique_zips * len_unique_zips)

    def test__get_mean_zip_time(self):
        """Test method which calculates average-fare for each zipcode
        """

        obj = CalculateTravelTimes(False, TIME_PERIODS,
                                   df_path=DF_PATH)

        average_travel_df = obj._get_mean_zip_time(obj.df,
                                                   AVERAGE_DF_PATH,
                                                   TIME_PERIODS)

        zip_10026_df = average_travel_df[(average_travel_df['pickup_zips']) ==
                                         10026]
        self.assertTrue(np.mean(zip_10026_df['mean_zone_time']) == 2)

        zip_10030_df = average_travel_df[(average_travel_df['pickup_zips']) ==
                                         10030]
        self.assertTrue(np.mean(zip_10030_df['mean_zone_time']) == 4)

        zip_10031_df = average_travel_df[(average_travel_df['pickup_zips']) ==
                                         10031]
        self.assertTrue(np.mean(zip_10031_df['mean_zone_time']) == 0)

    def test_return_average_travel_time(self):
        """Method to test if dictionary is being looking up correctly

        """
        obj = CalculateTravelTimes(TIME_PERIODS,
                                   average_df_path=AVERAGE_DF_PATH)
        dt1 = dt.datetime(2017, 8, 9, 0, 56, 40, 796658)
        dt2 = dt.datetime(2017, 8, 9, 4, 56, 40, 796658)
        dt3 = dt.datetime(2017, 8, 9, 9, 56, 40, 796658)
        dt4 = dt.datetime(2017, 8, 9, 13, 56, 40, 796658)
        dt5 = dt.datetime(2017, 8, 9, 19, 56, 40, 796658)
        dt6 = dt.datetime(2017, 8, 9, 22, 56, 40, 796658)

        result1 = obj.return_average_travel_time(dt1)
        result2 = obj.return_average_travel_time(dt2)
        result3 = obj.return_average_travel_time(dt3)
        result4 = obj.return_average_travel_time(dt4)
        result5 = obj.return_average_travel_time(dt5)
        result6 = obj.return_average_travel_time(dt6)
        self.assertTrue(result1[10026] == 2)
        self.assertTrue(result2[10027] == 1)
        self.assertTrue(result3[10028] == 3)
        self.assertTrue(result4[10029] == 0)
        self.assertTrue(result5[10030] == 4)
        self.assertTrue(result6[10031] == 0)


if __name__ == '__main__':
    unittest.main()
