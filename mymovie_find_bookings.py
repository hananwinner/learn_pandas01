import pandas as pd
import datetime
import time
import matplotlib.pyplot as plt
import numpy as np
import logging
from utils import make_logger


def parse_day(day_str):
    return datetime.datetime.strptime(day_str, "%Y/%m/%d")

def read_timeslot():
    df = pd.read_csv('user_timeslot.csv', index_col=['user_id'],
                     dtype={'user_id': 'object',
                            # 'timestamp': 'float64',
                            'day': 'object'})
    df['day'] = df["day"].apply(parse_day)
    return df

def read_user_interest():
    df = pd.read_csv('user_interest.csv', index_col=['user_id'],
                     dtype={'user_id': 'object',
                            # 'timestamp': 'float64',
                            'title_id': 'object', 'total_bid': 'int64'})
    return df


class BidCalculator(object):
    def __init__(self, minimal_bid, df_user_interest, df_user_timeslot, **kwargs):
        self._df = None
        self._minimal_bid = minimal_bid
        self._df_user_interest = df_user_interest
        self._df_user_timeslot = df_user_timeslot
        self._bids_found = 0
        self._users_booked = 0
        log_arg = kwargs.get("log")
        log_level_arg = kwargs.get("log_level")
        self._log = make_logger(log_arg, log_level_arg, clear_file=True)

    def _prepare_data(self):
        self._df = pd.merge(self._df_user_timeslot, self._df_user_interest, on=['user_id'])

    def _calc(self):
        while True:
            best = self.group_bids()
            best_title_and_date = best.index[0]
            best_bid = best.loc[best_title_and_date, 'total_bid']
            if best_bid < self._minimal_bid:
                break
            else:
                self._bids_found += 1
                best_day, best_title_id = best_title_and_date

                self._log.info('best_day', best_day.strftime("%Y/%m/%d"))
                self._log.info('best_title_id', best_title_id)
                self._log.info('bid', str(best_bid))

                booked_users = set()

                self.clear_bookings(best_day, best_title_id, booked_users)

                self.clear_booked_days(best_day, booked_users)

    def clear_booked_days(self, best_day, booked_users):
        self._df['total_bid'] = [
            np.nan if row[1][0] == best_day and row[0] in booked_users else row[1][2]
            for row in self._df.iterrows()
        ]
        for ind, vals in self._df.iterrows():
            if np.isnan(vals[2]):
                user_id = ind
                day = vals[0]
                title = vals[1]
                self._event_booking_canceled(user_id, day, title,
                                             reason="user already booked this day to another title")
        self._df = self._df.dropna(how='any')

    def clear_bookings(self, best_day, best_title_id, booked_users):
        self._df['total_bid'] = [
            np.nan if row[1][0] == best_day and row[1][1] == best_title_id else row[1][2]
            for row in self._df.loc[:, ['day', 'title_id', 'total_bid']].iterrows()
        ]
        for ind, vals in self._df.iterrows():
            if np.isnan(vals[2]):
                user_id = ind
                day = vals[0]
                title = vals[1]
                self._event_user_booked(user_id, day, title)
                booked_users.add(user_id)
        self._df = self._df.dropna(how='any')

    def group_bids(self):
        best = self._df.groupby(['day', 'title_id']).sum(columns=['total_bid'])
        best = best.sort_values(by='total_bid', ascending=False)
        return best

    def _event_user_booked(self, user_id, day, title_id):
        self._users_booked += 1
        self._log.debug('event_user_booked', user_id, day.strftime("%Y/%m/%d"), title_id)

    def _event_booking_canceled(self, user_id, day, title_id, reason=None):
        self._log.debug('event_booking_canceled', user_id, day.strftime("%Y/%m/%d"), title_id, reason)

    def main(self):
        self._prepare_data()
        self._calc()


if __name__ == "__main__":
    interest = read_user_interest()
    timeslot = read_timeslot()
    min_bid = 1200
    calc = BidCalculator(min_bid, interest, timeslot, log='.', log_level=logging.INFO)
    calc.main()









