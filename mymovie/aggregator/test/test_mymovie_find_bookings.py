from unittest import TestCase
import time
import logging
import yaml
import copy
from mymovie.aggregator.config import Config
from mymovie.aggregator.mymovie_create_input import \
    create_file, SampleDB, UserInterestEntryMaker, CreateTimeSlotEntry
from mymovie.aggregator.mymovie_find_bookings import read_timeslot, read_user_interest

class TestBidCalculator(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def read_input(self):
        self._interest = read_user_interest()
        self._timeslot = read_timeslot()

    def _gen_input(self,
                   total_users,
                   user_interest_rows,
                   total_titles,
                   user_timeslot_rows,
                   fixed_bid):
        db = SampleDB(num_user=total_users, num_title=total_titles)
        create_file('user_interest.csv', user_interest_rows,
                    UserInterestEntryMaker(db,
                                           single_ticket_bid_low=fixed_bid,
                                           single_ticket_bid_high=fixed_bid))
        create_file('user_timeslot.csv', user_timeslot_rows,
                    CreateTimeSlotEntry(db))

    # def test_variable_availability(self):
    #     base_config = {
    #         'total_users': 2000,
    #         'user_interest_rows': 4000,
    #         'total_titles': 30,
    #         'user_timeslot_rows': -1,
    #         'fixed_bid': 10,
    #         'min_group_bid': 300,
    #         'test_name': 'standard'
    #     }
    #     user_timeslot_params = []

    def test_num_users(self):
        base_config = {
            'total_users': -1,
            'user_interset_multiplier': 0.2,
            'user_timeslot_multiplier_per_day': 0.143,
            'time_period_days': 14,
            'total_titles': 20,
            'fixed_bid': 10,
            'min_group_bid': 300,
            'test_name': 'variable_user-20_titles'
        }
        user_num_params = range(500, 5000+1, 500)
        configs = []
        for num_user in user_num_params:
            config = copy.copy(base_config)
            config['total_users'] = num_user
            config = Config(config)
            configs.append(config)
        out_file = base_config['test_name'] + '_results.csv'
        for config in configs:
            self._test_main(config, out_file)


    def _test_fixture_files(self):
        base_path = ''
        configs = []
        for file in os.listdir(base_path):
            full_path = os.path.join(base_path,file)
            if os.path.isfile(full_path):
                with open(full_path, 'r') as fdr:
                    config = yaml.load(fdr)
                config = Config(config)
                configs.append(config)
        for config in configs:
            self._test_main(config)

    def _test_main(self, config, out_file='test_result.csv'):
        start_time = time.time()
        total_titles = config['total_titles']
        total_users = config['total_users']
        self._gen_input(total_users,
                        config['user_interest_rows'],
                        total_titles,
                        config['user_timeslot_rows'],
                        config['fixed_bid'])
        start_read = time.time()
        gen_input_duration = start_read - start_time
        self.read_input()
        start_process = time.time()
        read_duration = start_process - start_read
        min_group_bid = config['min_group_bid']
        calc = BidCalculator(min_group_bid, self._interest, self._timeslot,
                             log='.', log_level=logging.INFO)
        calc.main()
        end_process = time.time()
        process_duration = end_process - start_process
        log_test_result(
            start_time, end_process, end_process -start_time,
                              gen_input_duration, read_duration, process_duration,
                              config,
                              calc._bids_found, calc._users_booked, calc._total_bids,
            calc._total_unique_users,
                                out_file)
