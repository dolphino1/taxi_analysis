import unittest
import pandas as pd
from datetime import datetime
from driver_comparison.driver_comparison import DriverComparison

TEST_DATA_PATH = 'src/driver_comparison/tests/driver_comparison_test_data/'


class DriverComparisionTestCase(unittest.TestCase):

    def setUp(self):
        self.obj = DriverComparison(
            csv_path=TEST_DATA_PATH + 'driver_comparison_dummy_data.csv',
            void_taxi_param=30)

    def test_filter_date(self):
        start_test_date = datetime(1994, 4, 3, 2, 44, 1)
        end_test_date = datetime(1994, 4, 3, 2, 44, 1)

        result = self.obj.filter_date(self.obj.data,
                                      start_test_date,
                                      end_test_date)

        start_test_date = datetime(2013, 1, 5, 3, 44, 1)
        end_test_date = datetime(2013, 1, 5, 17, 44, 1)

        result = self.obj.filter_date(self.obj.data,
                                      start_test_date,
                                      end_test_date)

        start_test_date = datetime(2013, 1, 5, 3, 44, 1)
        end_test_date = datetime(2013, 1, 5, 17, 44, 1)

        result = self.obj.filter_date(self.obj.data,
                                      start_test_date,
                                      end_test_date)

        start_time = datetime(2013, 1, 5, 18, 27, 1)
        end_time = datetime(2013, 1, 5, 21, 6, 1)

        result = self.obj.filter_date(self.obj.data,
                                      start_time,
                                      end_time)

        self.assertTrue(len(result) == 2)

    def test_average_earnings(self):
        start_time = datetime(2013, 1, 5, 8, 47, 1)
        end_time = datetime(2013, 1, 5, 10, 36, 1)

        result = self.obj.average_earnings(start_time,
                                           end_time)

        self.assertTrue(result == 11.0)

        start_time = datetime(2013, 1, 5, 9, 15, 1)
        end_time = datetime(2013, 1, 5, 10, 36, 1)

        result = self.obj.average_earnings(start_time,
                                           end_time)

        self.assertTrue(result == 9.0)

        start_time = datetime(2013, 1, 5, 18, 27, 1)
        end_time = datetime(2013, 1, 5, 21, 6, 1)

        self.obj.void_taxi_param = 60

        result = self.obj.average_earnings(start_time,
                                           end_time)

        self.assertTrue(result == 16.0)

        start_time = datetime(1916, 1, 5, 18, 27, 1)
        end_time = datetime(1916, 1, 5, 21, 6, 1)

        with self.assertRaises(Exception) as context:
            self.obj.average_earnings(start_time, end_time)

        self.assertTrue("No Drivers Worked Shift" in str(context.exception))

    def test_filter_void_medallions(self):
        start_time = datetime(2013, 1, 5, 8, 47, 1)
        end_time = datetime(2013, 1, 5, 10, 36, 1)

        meds_df = self.obj.filter_void_medallions(self.obj.data,
                                                  start_time, end_time)

        self.assertTrue(len(meds_df) == 3)

        start_time = datetime(2013, 1, 5, 18, 27, 1)
        end_time = datetime(2013, 1, 5, 21, 6, 1)

        meds_df = self.obj.filter_void_medallions(self.obj.data,
                                                  start_time, end_time)
        self.assertTrue(len(meds_df) == 0)

        obj_longer_break_time = DriverComparison(
            csv_path=TEST_DATA_PATH + 'driver_comparison_dummy_data.csv',
            void_taxi_param=60)

        meds_df = obj_longer_break_time.filter_void_medallions(self.obj.data,
                                                               start_time,
                                                               end_time)

        self.assertTrue(len(meds_df) == 2)

    def test_high_breaks(self):

        pickup_times = [datetime(2013, 1, 3, 5, 7, 1),
                        datetime(2013, 1, 3, 6, 2, 1),
                        datetime(2013, 1, 3, 6, 27, 1)]

        dropoff_times = [datetime(2013, 1, 3, 5, 20, 1),
                         datetime(2013, 1, 3, 6, 10, 1),
                         datetime(2013, 1, 3, 6, 50, 1)]

        shift_df = {'pickup_datetime': pickup_times,
                    'dropoff_datetime': dropoff_times}

        shift_df = pd.DataFrame(shift_df)
        max_break = 30

        should_be_true = self.obj.high_breaks(shift_df, max_break)
        self.assertTrue(should_be_true)

        max_break = 45

        should_be_false = self.obj.high_breaks(shift_df, max_break)
        self.assertFalse(should_be_false)

    def test_shift_started_on_time(self):
        pickup_times = [datetime(2013, 1, 3, 5, 7, 1),
                        datetime(2013, 1, 3, 6, 2, 1),
                        datetime(2013, 1, 3, 6, 27, 1)]

        dropoff_times = [datetime(2013, 1, 3, 5, 20, 1),
                         datetime(2013, 1, 3, 6, 10, 1),
                         datetime(2013, 1, 3, 6, 50, 1)]

        shift_df = {'pickup_datetime': pickup_times,
                    'dropoff_datetime': dropoff_times}

        shift_df = pd.DataFrame(shift_df)

        start_time = datetime(2013, 1, 3, 4, 45, 1)
        on_time = self.obj.shift_started_on_time(shift_df, start_time, 30)

        self.assertTrue(on_time)
        on_time = self.obj.shift_started_on_time(shift_df, start_time, 10)
        self.assertFalse(on_time)

    def test_shift_ended_on_time(self):
        pickup_times = [datetime(2013, 1, 3, 5, 7, 1),
                        datetime(2013, 1, 3, 6, 2, 1),
                        datetime(2013, 1, 3, 6, 27, 1)]

        dropoff_times = [datetime(2013, 1, 3, 5, 20, 1),
                         datetime(2013, 1, 3, 6, 10, 1),
                         datetime(2013, 1, 3, 6, 50, 1)]

        shift_df = {'pickup_datetime': pickup_times,
                    'dropoff_datetime': dropoff_times}

        shift_df = pd.DataFrame(shift_df)

        end_time = datetime(2013, 1, 3, 6, 55, 1)
        on_time = self.obj.shift_ended_on_time(shift_df, end_time, 30)

        self.assertTrue(on_time)
        on_time = self.obj.shift_ended_on_time(shift_df, end_time, 3)
        self.assertFalse(on_time)


if __name__ == '__main__':
    unittest.main()
