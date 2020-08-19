from pyspark import SparkContext, SparkConf

import datetime
import time
import logging
from mymovie.aggregator.utils import make_logger

minimal_venue_cost = 15


conf = SparkConf().setAppName("myspark").setMaster("local[*]")
sc = SparkContext(conf=conf)



def make_input():
    bids_by_user = []
    bids_by_show = []
    with open("data.txt","r") as fdr:
        for line in fdr.readlines():
            parts = line.split(' ')
            if len(parts) == 5:
                _pair_by_show = ((parts[1], parts[2], parts[3]), int(parts[4]))
                _pair_by_user = ((parts[0]), (parts[1], parts[2], parts[3], parts[4]))

    bids_by_user = sc.parallelize(bids_by_user)
    bids_by_show = sc.parallelize(bids_by_show)
    return bids_by_user, bids_by_show

class SparkAgg(object):


    def __init__(self, **kwargs):
        self._bids_by_user = None
        self._bids_by_show = None
        log_arg = kwargs.get("log")
        log_level_arg = kwargs.get("log_level")
        self._log = make_logger(log_arg, log_level_arg, clear_file=True)

    def event_maximal_bid(self, _sum, t, ts, ven):
        self._log.info("Request to seat show. total bids sum:{}\n{}@{}@{}"
                       .format(_sum, t, ven, ts))
        booked_users = self._bids_by_user.filter(lambda x: x[0][0] == t and x[0][1] == ts and x[0][2] == ven)


    def main(self):
        self._bids_by_user, self._bids_by_show = make_input()
        while True:
            best_total_bids = self._bids_by_show.reduceByKey(lambda a, b: a + b)
            x = best_total_bids.takeOrdered(1, key=lambda x: -x[-1])
            if not x or x[-1] < minimal_venue_cost:
                break
            max_total_bids = x[-1]
            title_max, ts_max, venue_max = x[0]
            self.event_maximal_bid(max_total_bids, title_max, ts_max, venue_max)




print(x)