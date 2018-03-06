import numpy as np
from datetime import timedelta

CASH_RATE = 1


class TaxiEnvironment():
    """The purpose of this class is to provide a wrapper for running a
        simulation of a taxi environment.
    """

    def __init__(self, simulate_trip_func, simulate_wait_func,
                 simulate_travel_func, cash_rate=CASH_RATE):
        """
            simulate_trip_func: given a zip code and the datetime returns
                a new zip code (representing a customer trip to that zip code)
            simulate_wait_func: given a zip code and a datetime returns
                a time in minutes (representing the time the driver spent
                searching for a customer)
            simulate_travel_func: given 2 zip codes and a datetime estimates
                how long it would take to travel form the first zip code to
                the second
            cash_rate: fare per minute

        """

        self.cash_rate = cash_rate

        self.simulate_trip_func = simulate_trip_func
        self.new_wait = simulate_wait_func
        self.new_travel_time = simulate_travel_func
        self.zip_code_travel_history = []

    def run(self, start_zip, start_datetime, end_datetime, decision_func,
            rand_generator=np.random.rand):
        """Run the simulation of the new york taxi environment

            Args:
                start_zip: location_ taxi starts in
                start_datetime: time of day the taxi begins shift at
                end_datetime: time of day the taxi ends shit at
                decision_func: function that decides where a taxi should move
                    to next given the current location and current zip
                random_generator: should generate a number between 0 and 1
                    when called

            Returns:
                total_fare: the total money the taxi driver earned over the
                    course of the journeys

        """
        self.zip_code_travel_history = []
        self.time_history = []

        self.current_zip = start_zip
        self.current_time = start_datetime
        self.end_time = end_datetime

        total_fare = 0
        done = False

        while(not done):
            self.zip_code_travel_history.append(self.current_zip)
            zip_choice = decision_func(self.current_zip, self.current_time)

            self.zip_code_travel_history.append(zip_choice)
            obs = self.step(zip_choice, rand_generator=rand_generator)

            done = obs['done']
            self.time_history.append(self.current_time)
            total_fare += obs['fare']

        return total_fare

    def step(self, zip_code, rand_generator=np.random.rand):
        """Take next step in simmulation:

            Args:
                zip_code: zip code taxi should travel to next
                rand_generator: used to make the simulation stocastic, should
                    return 0 - 1 random number when called

            Returns:
                observation: dictionary record of the trip
                    time: -> time elapsed in minutes
                    fare: -> money made on trip
                    done: -> boolean, is the drivers shift up?
        """

        # Travel to zip
        time_traveling_to_new_zone = self.new_travel_time(self.current_zip,
                                                          zip_code,
                                                          self.current_time)
        # Wait for customer
        time_waiting_for_customer = self.new_wait(zip_code, self.current_time)

        # Take trip with customer
        new_zip = self.simulate_trip_func(zip_code,
                                          self.current_time,
                                          rand_generator())

        self.current_zip = new_zip
        time_trip_time = self.new_travel_time(zip_code, new_zip,
                                              self.current_time)

        total_time = (time_traveling_to_new_zone
                      + time_waiting_for_customer
                      + time_trip_time)

        self.current_time += timedelta(minutes=total_time)

        if(self.current_time > self.end_time):
            observation = dict({
                'time': 0,
                'fare': 0,
                'done': True
            })

            return observation

        else:
            fare = time_trip_time * self.cash_rate

            observation = dict({
                'time': total_time,
                'fare': fare,
                'done': False
            })

            return observation
