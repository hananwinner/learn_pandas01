import pandas as pd
import datetime
import time
import matplotlib.pyplot as plt
import numpy as np


class BidCalculator(object):
    def __init__(self):
        self._df = None
        self._minimal_bid = 500

    @staticmethod
    def parse_day(day_str):
        return datetime.datetime.strptime(day_str, "%Y/%m/%d")

    @staticmethod
    def read_timeslot():
        df = pd.read_csv('user_timeslot.csv', index_col=['user_id'],
                         dtype={'user_id': 'object',
                                # 'timestamp': 'float64',
                                'day': 'object'})
        df['day'] = df["day"].apply(BidCalculator.parse_day)
        return df

    @staticmethod
    def read_user_interest():
        df = pd.read_csv('user_interest.csv', index_col=['user_id'],
                         dtype={'user_id': 'object',
                                # 'timestamp': 'float64',
                                'title_id': 'object', 'total_bid': 'int64'})
        return df

    def _prepare_data(self):
        df = self.read_timeslot()
        df2 = self.read_user_interest()
        self._df = pd.merge(df, df2, on=['user_id'])

    def _calc(self):
        while True:
            best = self._df.groupby(['day', 'title_id']).sum(columns=['total_bid'])
            best = best.sort_values(by='total_bid', ascending=False)
            best_title_and_date = best.index[0]
            best_bid = best.loc[best_title_and_date, 'total_bid']
            if best_bid < self._minimal_bid:
                break
            else:
                best_day, best_title_id = best_title_and_date

                print('best_day', best_day)
                print('best_title_id', best_title_id)

                booked_users = set()

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

    def _event_user_booked(self, user_id, day, title_id):
        print('event_user_booked', user_id, day, title_id)

    def _event_booking_canceled(self, user_id, day, title_id, reason=None):
        print('event_booking_canceled', user_id, day, title_id, reason)

    def main(self):
        self._prepare_data()
        self._calc()


if __name__ == "__main__":
    calc = BidCalculator()
    calc.main()









