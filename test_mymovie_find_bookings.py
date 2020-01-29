from unittest import TestCase
from mymovie_find_bookings import *
import time
import inspect
from mymovie_create_input import *
import logging
import os
import yaml


class TestBidCalculator(TestCase):
    def setUp(self):
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print('%s: %.3f' % (self.id(), t))

    def read_input(self):
        self._interest = read_user_interest()
        self._timeslot = read_timeslot()
        t = time.time() - self.startTime
        print('%s: %.3f' % (inspect.currentframe().f_code.co_name, t))
        self.startTime = time.time()

    def _gen_input(self,
                   total_users,
                   user_interest_rows,
                   total_titles,
                   user_timeslot_rows,
                   fixed_bid):
        db = InputMaker(num_user=total_users, num_title=total_titles)
        create_file('user_interest.csv', user_interest_rows,
                    UserInterestEntryMaker(db, fixed_bid))
        create_file('user_timeslot.csv', user_timeslot_rows,
                    CreateTimeSlotEntry(db))
        t = time.time() - self.startTime
        print('%s: %.3f' % (inspect.currentframe().f_code.co_name, t))
        self.startTime = time.time()

    def test_(self):
        base_path = 'test'
        configs = []
        for file in os.listdir(base_path):
            config = {}
            with open(os.path.join(base_path,file), 'r') as fdr:
                config = yaml.load(fdr)
            configs.append(config)
        for config in configs:
            self._test_main(config)

    def _test_main(self, config):
        self._gen_input(config['total_users'],
                        config['user_interest_rows'],
                        config['total_titles'],
                        config['user_timeslot_rows'],
                        config['fixed_bid'])
        self.read_input()
        min_group_bid = config['min_group_bid']
        calc = BidCalculator(min_group_bid, self._interest, self._timeslot,
                             log='.', log_level=logging.INFO)
        calc.main()
        print('bids_found:',calc._bids_found)
        print('user_booked:', calc._users_booked)
