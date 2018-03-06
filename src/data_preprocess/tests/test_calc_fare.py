import unittest
from src.data_preprocess.calc_mean_fare import CalculateFare
import datetime as dt
import numpy as np

TIME_PERIODS = 6
DF_PATH = 'src/data_preprocess/tests/calc_fare_test_data/test_fare.csv'
FARE_PATH = 'src/data_preprocess/tests/calc_fare_test_data/'
FARE_PATH += 'test_average_fare_df.pkl'


class CalcTravelTimeTestCase(unittest.TestCase):

    def test__calc_average_zip_fare(self):
        """Test method which calculates average-fare for each zipcode
        """

        obj = CalculateFare(False, TIME_PERIODS,
                            df_path=DF_PATH)

        average_fare_df = obj._calc_average_zip_fare(obj.df,
                                                     FARE_PATH,
                                                     TIME_PERIODS)

        zip_10026_df = average_fare_df[(average_fare_df['pickup_zips']) ==
                                       10026]
        self.assertTrue(np.mean(zip_10026_df['mean_zone_fare']) == 20)

        zip_10030_df = average_fare_df[(average_fare_df['pickup_zips']) ==
                                       10030]
        self.assertTrue(np.mean(zip_10030_df['mean_zone_fare']) == 40)

        zip_10031_df = average_fare_df[(average_fare_df['pickup_zips']) ==
                                       10031]
        self.assertTrue(np.mean(zip_10031_df['mean_zone_fare']) == 0)

    def test_return_average_fare(self):
        """Method to test if dictionary is being looking up correctly

        """
        obj = CalculateFare(TIME_PERIODS, fare_path=FARE_PATH)
        dt1 = dt.datetime(2017, 8, 9, 9, 56, 40, 796658)
        dt2 = dt.datetime(2017, 8, 9, 11, 56, 40, 796658)

        result1 = obj.return_average_fare(dt1)
        result2 = obj.return_average_fare(dt1)
        result3 = obj.return_average_fare(dt1)
        result4 = obj.return_average_fare(dt2)
        result5 = obj.return_average_fare(dt2)

        self.assertTrue(result1[10028] == 180)
        self.assertTrue(result2[10027] == 60)
        self.assertTrue(result3[10026] == 120)
        self.assertTrue(result4[10029] == 0)
        self.assertTrue(result5[10030] == 240)


if __name__ == '__main__':
    unittest.main()
