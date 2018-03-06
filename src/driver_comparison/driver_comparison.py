import pandas as pd
from datetime import timedelta

CSV_PATH = 'data/zips_manhattan.csv'
VOID_TAXI_PARAM = 35


class DriverComparison():
    """
        The purpose of this class is calculate the performance of drivers
        in the new york taxi data set for different time periods.

        Drivers who take long gaps between their dropoffs and next pickup are
        assumed not to be working.

        NOTE: I will need to take out drivers who had a high waiting time
        between shifts
    """

    def __init__(self, csv_path=CSV_PATH, void_taxi_param=VOID_TAXI_PARAM):
        """
            On initialisation past booking data from a csv file is loaded
            and processed in a pandas dataframe.

            Args:
                csv_path: string path to past booking data
                void_taxi_param: A taxi is considered not to be working the
                    shift if there are any gaps in between a drop off and
                    next pickup greater than this (int) in minutes

            Attributes:
                data: pandas dataframe containing past booking data
                    with datetime columns
                void_taxi_param: see above
        """
        self.data = pd.read_csv(csv_path, skipinitialspace=True)
        self.data['pickup_datetime'] = pd.to_datetime(
            self.data['pickup_datetime'])
        self.data['dropoff_datetime'] = pd.to_datetime(
            self.data['dropoff_datetime'])
        self.data = self.data.sort_values(by='pickup_datetime')

        self.void_taxi_param = void_taxi_param

    def average_earnings(self, start_shift, end_shift):
        """
            Return the average earnings for taxi drivers in the dataset
            between too dates.

            Args:
                start_shift: datetime the taxi driver should at least be
                    working from
                end_shift: datetime the taxi driver should at least be working
                    up to
        """
        filtered_df = self.filter_date(self.data, start_shift, end_shift)
        filtered_df = self.filter_void_medallions(filtered_df,
                                                  start_shift,
                                                  end_shift)

        n_medallions = len(filtered_df['medallion'].unique())
        if n_medallions < 1:
            raise Exception("No Drivers Worked Shift")

        return filtered_df['fare_amount'].sum() / n_medallions

    def total_trip_time(self, start_shift, end_shift):
        filtered_df = self.filter_date(self.data, start_shift, end_shift)
        filtered_df = self.filter_void_medallions(filtered_df,
                                                  start_shift,
                                                  end_shift)

        n_medallions = len(filtered_df['medallion'].unique())
        if n_medallions < 1:
            raise Exception("No Drivers Worked Shift")

        return (filtered_df['trip_time_in_secs'].sum() / n_medallions) / 60

    def compare(self, start_shift, end_shift):
        filtered_df = self.filter_date(self.data, start_shift, end_shift)
        filtered_df = self.filter_void_medallions(filtered_df,
                                                  start_shift,
                                                  end_shift)
        n_medallions = len(filtered_df['medallion'].unique())

        if n_medallions < 1:
            return {
                'n_medallions': n_medallions,
                'original_data_frame': filtered_df,
                'average_fare': 0,
                'average_drive_time': 0
            }
        else:
            average_driving_time = ((filtered_df['trip_time_in_secs'].sum()
                                    / n_medallions) / 60)

            average_fare = filtered_df['fare_amount'].sum() / n_medallions
            return {
                'n_medallions': n_medallions,
                'average_drive_time': average_driving_time,
                'average_fare': average_fare,
                'medallions': (filtered_df.groupby('medallion')[['trip_time_in_secs', 'fare_amount']].sum())
            }

    @staticmethod
    def filter_date(data, start_shift, end_shift):
        """
            Filters dataframe dates not in pickup range.
        """
        filtered = data[data['pickup_datetime'] > start_shift]
        filtered = filtered[filtered['pickup_datetime'] < end_shift]

        return filtered

    def filter_void_medallions(self, data, start_shift, end_shift):
        """
            Given past bookings data this function will remove all rows
            with medallions (taxis license numbers) that were not considered
            to be working the shift.

            A taxi is considered not to be working the shift if
            1)There are any gaps in between a drop off and next pickup greater
             than the void_taxi_param in minutes
            2)Did not make a pickup within start shift + void_taxi_param
            3)Did not make a pickup within end shift - void_taxi_param

            These conditions are checked with the 3 static functions found
            below this method.

            Args:
                start_shift: datetime shift started at
                end_shift: datetime shift eneded at

            Returns:
                pandas dataframe with void taxis filtered out
        """

        void_list = []

        for med in data['medallion'].unique():
            subset = data[data['medallion'] == med]

            max_break = self.void_taxi_param
            pass_conditions = \
                [self.shift_started_on_time(subset, start_shift, max_break),
                 self.shift_ended_on_time(subset, end_shift, max_break),
                 not self.high_breaks(subset, max_break)]

            if not all(pass_conditions):
                void_list.append(med)

        return data[~data['medallion'].isin(void_list)]

    @staticmethod
    def high_breaks(medallion_subset, max_break):
        """
            Args:
                medallion_subset: past booking data containing only 1
                    medallion number
                max_break: max allowable difference between journeys

            Returns:
                True if there are any gaps between a pickup and its next drop
                off greater than max break,
                False if there are no gaps.
        """
        shift_pickup = medallion_subset.pickup_datetime.shift(-1)
        time_searching = shift_pickup - medallion_subset.dropoff_datetime
        void = time_searching > timedelta(minutes=max_break)

        return any(void)

    @staticmethod
    def shift_started_on_time(medallion_subset, start_shift, max_break):
        """
            Args:
                medallion_subset: past booking data containing only 1
                    medallion number
                start_shift: datetime shift starts
                max_breaks: max allowable gap between start of shift and first
                    pickup in minutes

            Returns:
                True if first pickup was before start_shift + max_break
        """
        must_start_by = start_shift + timedelta(minutes=max_break)
        first_trip = medallion_subset.iloc[0]['pickup_datetime']
        return first_trip <= must_start_by

    @staticmethod
    def shift_ended_on_time(medallion_subset, end_shift, max_break):
        """
            Args:
                medallion_subset: past booking data containing only 1
                    medallion number
                end_shift: datetime shift ends
                max_breaks: max allowable gap between the end of the shift and
                    the last pickup in minutes

            Returns:
                True if the last pickup was after end_shift - max_break
        """
        must_end_by = end_shift - timedelta(minutes=max_break)
        last_trip = medallion_subset.iloc[-1]['dropoff_datetime']
        return last_trip >= must_end_by
