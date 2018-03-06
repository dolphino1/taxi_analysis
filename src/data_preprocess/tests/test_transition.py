import unittest
from src.data_preprocess.transition import Transition
from datetime import datetime
import pandas as pd
import numpy as np

TEST_DATA_PATH = 'src/data_preprocess/tests/transition_test_data/'


class TransitionTestCase(unittest.TestCase):

    def test_map_to_period_calculates_period_correctly(self):
        date = datetime(1994, 4, 3, 2, 44, 1)
        time_periods = 4
        correct_index = 0
        test_index = Transition.map_to_period(date, time_periods)
        self.assertTrue(correct_index == test_index)

        date = datetime(1998, 2, 5, 23, 44, 1)
        time_periods = 4
        correct_index = 3
        test_index = Transition.map_to_period(date, time_periods)
        self.assertTrue(correct_index == test_index)

    # test calculate matrix calculates correct transition probabilites
    def test_calculate_matrix_calculates_correct_probabilities(self):
        zip_code_dict = {0: 0, 1: 1}

        df = pd.DataFrame({'pickup_zips': [0, 1], 'dropoff_zips': [0, 1]})
        matrix = Transition.calculate_matrix(df, zip_code_dict)

        correct_matrix = [[1, 0], [0, 1]]
        self.assertTrue(np.array_equal(matrix, correct_matrix))

        df = pd.DataFrame(
            {'pickup_zips': [0, 0, 1], 'dropoff_zips': [1, 0, 1]})
        matrix = Transition.calculate_matrix(df, zip_code_dict)

        correct_matrix = [[0.5, 0.5], [0, 1]]
        self.assertTrue(np.array_equal(matrix, correct_matrix))

    # test calculate matrices returns correct probabilities for different
    # time periods
    def test_calculate_matrices_correct_probabilities_diff_time_periods(self):
        obj = Transition(load_data=False,
                         zip_codes_path=TEST_DATA_PATH + 'DummyZipCodes.json',
                         csv_path=TEST_DATA_PATH + 'transition_dummy_data.csv',
                         pickle_path=(TEST_DATA_PATH +
                                      'dummy_matrices.pickle'),
                         time_periods=2)
        calculated_matrices = obj.matrices
        correct_matrices = [[1., 0.],
                            [0., 1.]], [[0., 1.],
                                        [0., 0.]]
        self.assertTrue(np.array_equal(calculated_matrices, correct_matrices))

    def test_saved_and_loaded_transition_matrices_are_equal(self):
        # obj_1 computes all matrices from scratch and saves them
        # to a pickle file
        obj_1 = Transition(
            load_data=False,
            zip_codes_path=TEST_DATA_PATH + 'DummyZipCodes.json',
            csv_path=TEST_DATA_PATH + 'transition_dummy_data.csv',
            pickle_path=TEST_DATA_PATH + 'dummy_matrices.pickle',
            time_periods=2)

        # obj_2 loads matrices from a pickle file path
        obj_2 = Transition(
            load_data=True,
            zip_codes_path=TEST_DATA_PATH + 'DummyZipCodes.json',
            csv_path=TEST_DATA_PATH + 'transition_dummy_data.csv',
            pickle_path=TEST_DATA_PATH + 'dummy_matrices.pickle',
            time_periods=2)

        saved_matrices = obj_1.matrices
        loaded_matrices = obj_2.matrices
        self.assertTrue(np.array_equal(saved_matrices, loaded_matrices))

    def test_simulate_new_dropoff_zone_returns_correct_zone(self):
        obj = Transition(
            load_data=False,
            zip_codes_path=TEST_DATA_PATH + 'DummyZipCodes.json',
            csv_path=TEST_DATA_PATH + 'transition_dummy_data.csv',
            pickle_path=TEST_DATA_PATH + 'dummy_matrices.pickle',
            time_periods=2)

        test_date = datetime(1994, 4, 3, 2, 44, 1)
        new_dropoff = obj.simulate_new_dropoff_zone(10026, test_date, 0.01)
        self.assertTrue(new_dropoff == 10026)

    def test_no_observations_returns_correct_boolean(self):
        obj = Transition(
            load_data=False,
            zip_codes_path=TEST_DATA_PATH + 'DummyZipCodes.json',
            csv_path=TEST_DATA_PATH + 'transition_dummy_data.csv',
            pickle_path=TEST_DATA_PATH + 'dummy_matrices.pickle',
            time_periods=2)
        test_date = datetime(1994, 4, 3, 13, 44, 1)
        should_be_true = obj.no_observations(10027, test_date)
        self.assertTrue(should_be_true)

        test_date = datetime(1994, 4, 3, 10, 44, 1)
        should_be_false = obj.no_observations(10027, test_date)
        self.assertFalse(should_be_false)


if __name__ == '__main__':
    unittest.main()
