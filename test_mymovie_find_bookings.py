from unittest import TestCase
from mymovie_find_bookings import *
import time
import inspect
from mymovie_create_input import *


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

    def _gen_input(self):
        create_file('user_interest.csv', 100, UserInterestEntryMaker())
        create_file('user_timeslot.csv', 300, CreateTimeSlotEntry())
        t = time.time() - self.startTime
        print('%s: %.3f' % (inspect.currentframe().f_code.co_name, t))
        self.startTime = time.time()

    def test_main(self):
        self._gen_input()
        self.read_input()
        min_bid = 500
        calc = BidCalculator(min_bid, self._interest, self._timeslot)
        calc.main()
        print('bids_found:',calc._bids_found)
        print('user_booked:', calc._users_booked)
