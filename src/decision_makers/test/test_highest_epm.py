import unittest
from datetime import datetime
from decision_makers.highest_epm import HighestEpm


class HighestEpmTestCase(unittest.TestCase):

    def setUp(self):
        # Set up Mock Dependencies
        def fake_average_search_dict_func(datetime):
            return {
                10026: 5,
                10027: 8,
            }

        def fake_distance_dict_func(zip, datetime):
            if zip == 10026:
                return {
                    10026: 1,
                    10027: 10
                }
            else:
                return {
                    10026: 10,
                    10027: 1
                }

        def fake_average_fare_dict_func(datetime):
            return {
                10026: 22,
                10027: 18
            }

        def fake_average_journey_length(datetime):
            return {
                10026: 11,
                10027: 8
            }

        self.obj = HighestEpm(fake_average_search_dict_func,
                              fake_distance_dict_func,
                              fake_average_fare_dict_func,
                              fake_average_journey_length)

    def test_choose_picks_highest_earnings_per_minute(self):
        test_date = datetime(1999, 4, 3, 2, 44, 1)
        choice = self.obj.choose(10026, test_date)

        self.assertTrue(choice == 10026)

        test_date = datetime(1999, 2, 3, 2, 44, 1)
        choice = self.obj.choose(10027, test_date)

        self.assertTrue(choice == 10027)


if __name__ == '__main__':
    unittest.main()
