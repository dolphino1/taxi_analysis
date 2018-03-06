import unittest
from taxi_environment.taxi_environment import TaxiEnvironment
from datetime import datetime


class TaxiEnvironmentTestCase(unittest.TestCase):

    def setUp(self):
        # Set up mock dependencies
        def fake_trip_func(zip_code, datetime, rand):
            if zip_code == 10026:
                return 10027
            else:
                return 10026

        def fake_wait_func(zip_code, datetime):
            return 5

        def fake_travel_func(zip_code_start, zip_code_end, datetime):
            return 10

        self.obj = TaxiEnvironment(
            fake_travel_func, fake_wait_func,
            fake_travel_func,
            cash_rate=0.5)

    def test_step_single_trip(self):
        self.obj.current_zip = 10027
        self.obj.current_time = datetime(1994, 4, 3, 13, 44, 1)
        self.obj.end_time = datetime(1994, 4, 3, 14, 20, 1)

        obs = self.obj.step(10026)

        self.assertFalse(obs['done'])
        self.assertTrue(obs['fare'] == 5)

        updated_object_time = self.obj.current_time
        correct_time = datetime(1994, 4, 3, 13, 49, 1)
        self.assertTrue(updated_object_time.date() == correct_time.date())

    def test_step_past_end_time(self):
        self.obj.current_zip = 10027
        self.obj.current_time = datetime(1994, 4, 3, 13, 44, 1)
        self.obj.end_time = datetime(1994, 4, 3, 13, 16, 1)

        obs = self.obj.step(10026)

        self.assertTrue(obs['done'])
        self.assertTrue(obs['fare'] == 0)

        updated_object_time = self.obj.current_time
        correct_time = datetime(1994, 4, 3, 13, 49, 1)
        self.assertTrue(updated_object_time.date() == correct_time.date())

    def test_run_past_end_time(self):
        start_date = datetime(1994, 4, 3, 13, 44, 1)
        end_date = datetime(1994, 4, 3, 13, 44, 1)

        def fake_decision_func(zip_code, datetime):
            if zip_code == 10026:
                return 10027
            else:
                return 10026

        total_fare = self.obj.run(10026, start_date, end_date,
                                  fake_decision_func)
        self.assertTrue(total_fare == 0)

    def test_run_one_trip(self):
        start_date = datetime(1994, 4, 3, 13, 44, 1)
        end_date = datetime(1994, 4, 3, 14, 10, 1)

        def fake_decision_func(zip_code, datetime):
            if zip_code == 10026:
                return 10027
            else:
                return 10026

        total_fare = self.obj.run(10026, start_date, end_date,
                                  fake_decision_func)
        self.assertTrue(total_fare == 5)

    def test_run_two_trips(self):
        start_date = datetime(1994, 4, 3, 13, 44, 1)
        end_date = datetime(1994, 4, 3, 14, 50, 1)

        def fake_decision_func(zip_code, datetime):
            if zip_code == 10026:
                return 10027
            else:
                return 10026

        total_fare = self.obj.run(10026, start_date, end_date,
                                  fake_decision_func)
        self.assertTrue(total_fare == 10)


if __name__ == '__main__':
    unittest.main()
