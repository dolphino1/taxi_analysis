import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize
import json
import pickle

TIME_PERIODS_IN_DAY = 6
CSV_PATH = 'data/zips_manhattan.csv'
ZIP_CODES_PATH = 'data/OrderedZipCodes.json'
PICKLE_PATH = 'data/trasition_matrices.pickle'


class Transition():
    """The transition class is used in the simulation to simulate the new drop
        off location given the current pickup location.

        In order to do this the class calculates all the probabilities of
        getting a fare from any given zip code to another zip code for each
        time period of the day. (Currently divided into 6)

        These probabilities matrices can be calculated on initialisation or
        loaded from a pickle file.

        The function simulate new drop off zone should be used to simulate
        the new trip destination. Given that the simulation is stocastic
        in nature a random number is used to choose the new drop off zone
        based on the precalculated probability weights.
    """

    def __init__(self, load_data=True, csv_path=CSV_PATH,
                 pickle_path=PICKLE_PATH, time_periods=TIME_PERIODS_IN_DAY,
                 zip_codes_path=ZIP_CODES_PATH):
        """
            Args:
                load_data: boolean should the probabilites be loaded from a
                pickle file (True) or calculated from a csv file(False)
                (if false will save to pickle path and override old file)
                csv_path: path to csv file with trip data
                pickle_path: path to pickle file where probabilites should be
                loaded from/ saved to.
                time_periods: How many time periods do we divide the day into
                and calculate seperate probability matrices  for.
                zip_codes_path: path to json file with ordered zip codes

            Attr:
                zip_dict: dictionary mapping zip codes to ordered indexes
                starting at 0
                matrices: transition probability matrices for each time period
                time_periods: How many time periods do we divide the day into
                and calculate seperate probability matrices  for.
        """

        with open(zip_codes_path) as data_file:
            zip_codes = json.load(data_file)['ZipCodes']

        self.zip_dict = dict(zip(zip_codes, np.arange(len(zip_codes))))

        # calculate probabilities
        if not load_data:
            self.matrices = self.calculate_matrices(
                csv_path, self.zip_dict, time_periods)
            with open(pickle_path, 'wb') as handle:
                pickle.dump(self.matrices, handle,
                            protocol=pickle.HIGHEST_PROTOCOL)

            self.time_periods = time_periods

        # load previously saved probability matrices
        else:
            with open(pickle_path, 'rb') as handle:
                self.matrices = pickle.load(handle)

            assert len(self.matrices) == time_periods, \
                "Loaded probabilites divide time periods into a different" \
                + "number of periods than was specified on initialisation"
            self.time_periods = time_periods

    def calculate_matrices(self, csv_path, zip_dict, time_periods):
        """Calculates all the probability transition matrices for each time
            period of the day.

            The matrices are stored as a list of matrices. The float found in
            Matrix index x row y column z represents the probability of
            transitioning from y to z given that you have just gotten a
            trip at time period x.

            Args:
                csv_path: path to csv file of past trips where probability
                matrices are calculated from.
                zip_dict: ordered dictionary of zipcodes to indexes, used
                to keep track of the indexes that the probabilites are
                located at in the matrices
                time_periods: number of matrices created for different time
                periods.

            Returns:
                List of transition probability matrices ordered by time period
        """

        csv_data = pd.read_csv(csv_path, skipinitialspace=True)
        # Need datetime not string
        csv_data['pickup_datetime'] = pd.to_datetime(
            csv_data['pickup_datetime'])

        csv_data['period'] = csv_data['pickup_datetime'].map(
            lambda datetime: self.map_to_period(datetime, time_periods))

        matrices = []
        for i in range(time_periods):
            sub_period = csv_data[csv_data['period'] == i]
            matrices.append(self.calculate_matrix(sub_period, zip_dict))
        return matrices

    @staticmethod
    def calculate_matrix(data_frame, zip_dict):
        """Calculate the probability transition matrix from pandas dataframe
            of taxi trips. Order the Zip codes according the the zip code
            dictionary.

            Row x Column y is the probability of transitioning from x to
            y.

            Args:
                data_frame: pandas dataframe containing taxi trips for a
                given time period
                zip_dict: dictionary of zipcode -> index order

            Returns:
                Matrix of transition probabilities
        """
        n = len(zip_dict)
        transition_matrix = np.zeros(shape=(n, n))

        def add_to_transition(row):
            """Helper function that takes in a past trip as an arg and
                updates the transition matrix selecting the location
                -> row that the taxi picked up
                -> column the taxi dropped off to
                and adding 1 to that location
            """
            pickup_zip = row['pickup_zips']
            dropoff_zip = row['dropoff_zips']

            matrix_row_index = zip_dict[pickup_zip]
            matrix_col_index = zip_dict[dropoff_zip]

            transition_matrix[matrix_row_index][matrix_col_index] += 1

        data_frame.apply(add_to_transition, axis=1)
        # Transition matrix now contains raw counts of trips
        # we normalize row wise to get probabilites
        return normalize(transition_matrix, axis=1, norm='l1')

    def simulate_new_dropoff_zone(self, current_zip_code, date_time, rand):
        """Returns the zip code where a passenger wants to travel to
            given that a taxi driver picks them up at a zip code.

            The zip code returned is based on transition probability weights
            calculated from past data and based on the current time of day.

            The random number provides a way to simulate which new zip code
            is choosen based on the calculated weights.

            Args:
                current_zip_code: the zip code where the taxi driver picks up
                the passenger from
                date_time: current time (datetime)
                rand: random number between 0 and 1

            Returns:
                drop_off_zip_code: new zip code passenger travels to
        """

        assert rand >= 0 and rand <= 1, "Random Number must be 0-1 scale"
        matrix_index = self.map_to_period(date_time, self.time_periods)
        time_period_matrix = self.matrices[matrix_index]

        vector_index = self.zip_dict[current_zip_code]
        zip_code_probabilities = time_period_matrix[vector_index]

        cdf = np.cumsum(zip_code_probabilities)
        new_vector_index = np.argmax(cdf > rand)

        drop_off_zip_code = list(self.zip_dict.keys())[new_vector_index]
        return drop_off_zip_code

    def no_observations(self, zip_code, date_time):
        """Method is used to see if there are any past observations for a
            given zip code.

            For example some zip codes have dropoffs but no
            pick ups in the data set. It is therefore impossible to know
            its transition probabilites based on historical data.

            The no_observations method provides a way of checking is this the
            case.

            If there are no observations for pickups in a given zip code
            it will be represented as a vector of zeros in the probability
            matrix.

            Args:
                zip_code: zip_code to check (int)
                date_time: time period of day to check for (datetime)

            Returns:
                boolean: no observations
        """
        matrix_index = self.map_to_period(date_time, self.time_periods)
        time_period_matrix = self.matrices[matrix_index]

        vector_index = self.zip_dict[zip_code]
        zip_code_probabilities = time_period_matrix[vector_index]

        return all(prob == 0 for prob in zip_code_probabilities)

    @staticmethod
    def map_to_period(datetime, time_periods):
        """Divides the day into n time_periods and returns the index of the
            the period the datetime falls into.

            Args:
                datetime: datetime to check
                time_periods: number of time periods to divide the day into

            Returns:
                index of time period: 0 -> time_periods - 1 (int)
        """
        decimal_hour = datetime.hour + (datetime.minute / 60)
        cut_offs = np.linspace(0, 24, time_periods + 1)
        return np.argmax(cut_offs >= decimal_hour) - 1
