from unittest import TestCase
from aggregator.mymovie_find_bookings import *
from aggregator.test.common_testing import *
import time
import pandas as pd
import datetime


class CorrectnessTest(TestCase):

    @staticmethod
    def parse_day(day_str):
        return datetime.datetime.strptime(day_str, "%Y/%m/%d")

    @staticmethod
    def read_input():
        _interest = pd.DataFrame({
            'user_id': pd.Series([1,1]),
            'title_id': pd.Series([1,2]),
            'total_bid': pd.Series(1, index=list(range(2)), dtype='float64')
        })
        _interest = _interest.set_index(keys=['user_id'])

        _timeslot = pd.DataFrame({
            'user_id': pd.Series([1, 1]),
            'day': pd.Series(['2020/02/02','2020/02/01',])
        })
        _timeslot['day'] = _timeslot["day"].apply(CorrectnessTest.parse_day)
        _timeslot = _timeslot.set_index(keys=['user_id'])
        return _interest, _timeslot

    def _test(self, input_func, min_group_bid, name=None):
        start_time = time.time()
        _interest, _timeslot = input_func()
        config = {
            'test_name': name or "correctness",
            'total_users': len(set(_interest.index)),
            'user_interest_rows': len(_interest),
            'total_titles': len(set(_interest['title_id'])),
            'user_timeslot_rows': len(_timeslot),
            'fixed_bid': 1,
            'min_group_bid': min_group_bid
        }
        min_group_bid = config['min_group_bid']
        calc = BidCalculator(min_group_bid, _interest, _timeslot,
                             log='.', log_level=logging.DEBUG)
        calc.main()
        # end_process = time.time()
        # process_duration = end_process - start_process
        out_file = 'logs/correctness_test.csv'
        log_test_result(
            start_time, -1, -1,
            -1, -1, -1,
            config,
            calc._bids_found, calc._users_booked, calc._total_bids, calc._total_unique_users,
            out_file)


    # def test1(self):
    #     self._test(self.read_input, 1)

    def test2(self):
        def read_input():
            _interest = pd.DataFrame({
                'user_id':  pd.Series([1, 1,
                                       2,2,
                                       3,
                                       4,4,
                                       5,
                                       1]),
                'title_id': pd.Series([1, 2,
                                       1,2,
                                       3,
                                       3,4,
                                       4,
                                       4,]),
                'total_bid': pd.Series(1, index=list(range(9)), dtype='float64')
            })
            _interest = _interest.set_index(keys=['user_id'])

            _timeslot = pd.DataFrame({
                'user_id': pd.Series([1, 1,
                                      2, 2,
                                      3,
                                      4,4,
                                      5,]),
                'day': pd.Series(['2020/02/02', '2020/02/01',
                                  '2020/02/02', '2020/02/03',
                                  '2020/02/01',
                                  '2020/02/01','2020/02/02',
                                  '2020/02/01',
                                  ])
            })
            _timeslot['day'] = _timeslot["day"].apply(CorrectnessTest.parse_day)
            _timeslot = _timeslot.set_index(keys=['user_id'])
            return _interest, _timeslot

        self._test(read_input, 2, "only movie 1 on day 2")

    # def test3(self):
    #     def read_input():
    #         _interest = pd.DataFrame({
    #             'user_id':  pd.Series([1, 1, 2, ]),
    #             'title_id': pd.Series([1, 2, 1]),
    #             'total_bid': pd.Series(1, index=list(range(3)), dtype='float64')
    #         })
    #         _interest = _interest.set_index(keys=['user_id'])
    #
    #         _timeslot = pd.DataFrame({
    #             'user_id': pd.Series([1, 1, 2, 2]),
    #             'day': pd.Series(['2020/02/02', '2020/02/01', '2020/02/02', '2020/02/03',])
    #         })
    #         _timeslot['day'] = _timeslot["day"].apply(parse_day)
    #         _timeslot = _timeslot.set_index(keys=['user_id'])
    #         return _interest, _timeslot
    #
    #     self._test(read_input, 2, "only movie 1 on day 2")


