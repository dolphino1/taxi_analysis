import numpy as np
ZIP_CODES_PATH = 'data/OrderedZipCodes.json'


class HighestEpm():
    """
        The purpose of this class is to choose the zone with the highest
        earnings per minute in order to tell the taxi driver where to drive.
    """

    def __init__(self, average_search_dict_func, distance_dict_func,
                 average_fare_dict_func, average_journey_length_func):
        """
            Args:
                average_search_dict_function: takes in a datetime and returns
                a dictionary containing the average search time for a taxi in
                each of the zip codes
                distance_vec_func: takes in a datetime and zip and returns a
                    dictionary containing the distances from provided zip code
                    to all other zip codes
                average_fare_dict_func: takes a datetime and returns
                    a dictionary of the average fares for all zip codes
                average_journey_length: takes a datetime and returns a
                    dictionary of the average journey length for all zip
                    codes
        """
        self.average_search_dict_func = average_search_dict_func
        self.distance_dict_func = distance_dict_func
        self.average_fare_dict_func = average_fare_dict_func
        self.average_journey_length_func = average_journey_length_func

    def choose(self, zip_code, datetime):
        """
            Choose the zip code we expect will make us the most money in the
            short term.

            ArgMax(
                average_zone_fare/
                    (searchtime + travel_time + ave_trip_time))

            Args:
                zip_code: zip code where the taxi currently is
                datetime: current datetime

            Returns:
                zip code with highest earnings per minute
        """

        average_search = self.average_search_dict_func(datetime)
        distances = self.distance_dict_func(zip_code, datetime)
        average_fare = self.average_fare_dict_func(datetime)
        average_journey_length = self.average_journey_length_func(datetime)

        dictionaries = [average_search, distances, average_fare,
                        average_journey_length]

        dictionaries = [dict(sorted(x.items())) for x in dictionaries]

        keys = [np.array(list(x.keys())) for x in dictionaries]
        values = [np.array(list(x.values())) for x in dictionaries]

        # Check are all keys equal
        #if not ((keys - keys[0]) == 0).all():
        #    raise Exception("Output keys from all functions did not match")

        # Time to drive to destination, search for passenger and drop
        # passenger off at destination
        total_time = values[0] + values[1] + values[3]

        # average value / total_time
        earnings_per_minute = values[2] / total_time

        highest_index = np.argmax(earnings_per_minute)

        return keys[0][highest_index]
