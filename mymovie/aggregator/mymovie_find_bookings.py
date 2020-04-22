import pandas as pd
import datetime
import time
import logging
from mymovie.aggregator.utils import make_logger
import boto3
import json


def parse_day(day_str):
    return datetime.datetime.strptime(day_str, "%Y/%m/%d")


def read_timeslot():
    df = pd.read_csv('user_timeslot.csv',
                     dtype={'user_id': 'object',
                            'day': 'object'})
    df['day'] = df["day"].apply(parse_day)
    df = df.drop_duplicates(subset=['user_id','day'])
    df = df.set_index(keys=['user_id'])
    return df


def read_user_interest():
    df = pd.read_csv('user_interest.csv',
                     dtype={'user_id': 'object',
                            'title_id': 'object', 'total_bid': 'int64'})
    df = df.drop_duplicates(subset=['user_id', 'title_id'])
    df = df.set_index(keys=['user_id'])
    return df


class BidCalculator(object):
    def __init__(self, minimal_bid, df_user_interest, df_user_timeslot,
                 event_handler=None, **kwargs):
        self._df = None
        self._minimal_bid = minimal_bid
        self._df_user_interest = df_user_interest
        self._df_user_timeslot = df_user_timeslot
        self._bids_found = 0
        self._total_bids = 0
        self._users_booked = 0
        self._total_unique_users = 0
        log_arg = kwargs.get("log")
        log_level_arg = kwargs.get("log_level")
        self._log = make_logger(log_arg, log_level_arg, clear_file=True)
        self._event_handler = event_handler

    def _prepare_data(self):
        self._df = self._df_user_interest.join(self._df_user_timeslot)
        self._df['status'] = 'A'

    def _calc(self):
        while True:
            best = self.group_bids()
            best_bids_total = best.loc[best.index[0], 'total_bid']
            if len(best) and best_bids_total > self._minimal_bid:
                best_title_and_date = best.index[0]
                best_bid = best.loc[best.index[0], 'total_bid']
                self._bids_found += 1
                self._total_bids += best_bid
                best_day, best_title_id = best_title_and_date

                self._log.info('best_day', best_day.strftime("%Y/%m/%d"))
                self._log.info('best_title_id', best_title_id)
                self._log.info('bid', str(best_bid))

                self.mark_booked_and_canceled(best_day, best_title_id, best_bids_total)
            else:
                break
        self._on_finish_stats()

    def _on_finish_stats(self):
        self._total_unique_users = self._df[self._df['status'] == 'B'].index.nunique()

    def mark_booked_and_canceled(self, day, title_id, bids_total):
        booked_users = set()

        self._df['status'] = [
            'BN'  # booked now
            if row[1]['day'] == day and row[1]['title_id'] == title_id and
            row[1]['status'] == 'A'
            else row[1]['status']
            for row in self._df.iterrows()
        ]

        df_booked_now = self._df[self._df['status'] == 'BN']

        num_booked_now = len(df_booked_now.index)
        self._event_event_booked(day, title_id, num_booked_now, bids_total)

        for row in df_booked_now.iterrows():
            user_id = row[0]
            booked_users.add(user_id)
            self._event_user_booked(user_id, row[1]['day'], row[1]['title_id'])

        self._df['status'] = [
            'CN'  # canceled now
            if (row[1]['day'] == day or row[1]['title_id'] == title_id) and
               row[0] in booked_users and row[1]['status'] == 'A'
            else row[1]['status']
            for row in self._df.iterrows()
        ]

        for row in self._df[self._df['status'] == 'CN'].iterrows():
            self._event_booking_canceled(row[0], row[1]['day'], row[1]['title_id'])

        def _mark_now_to_general(status):
            if status == 'BN':
                return 'B'
            elif status == 'CN':
                return 'C'
            else:
                return status

        self._df['status'] = self._df['status'].apply(_mark_now_to_general)

    def group_bids(self):

        if (self._df['status'] == 'A').any():
            best = \
                self._df[self._df['status'] == 'A'].loc[:,['day', 'title_id','total_bid']]\
                    .groupby(['day', 'title_id'])\
                    .sum(columns=['total_bid']) \
                    .sort_values(by='total_bid', ascending=False)
            return best
        else:
            return pd.DataFrame()

    def _event_user_booked(self, user_id, day, title_id):
        self._users_booked += 1
        day = day.strftime("%Y/%m/%d")
        if self._event_handler:
            self._event_handler.event_user_booked(user_id, day, title_id)
        self._log.debug('event_user_booked', user_id, day, title_id)

    def _event_booking_canceled(self, user_id, day, title_id, reason=None):
        day = day.strftime("%Y/%m/%d")
        if self._event_handler:
            self._event_handler.event_booking_canceled(user_id, day, title_id)
        self._log.debug('event_booking_canceled',
                        user_id, day, title_id, reason)

    def main(self):
        self._prepare_data()
        self._calc()

    def _event_event_booked(self, day, title_id, num_tickets, bids_total):
        day = day.strftime("%Y/%m/%d")
        if self._event_handler:
            self._event_handler.event_event_booked(day, title_id,
                                                   num_tickets, bids_total)
        self._log.debug('event_event_booked',
                        day, title_id)


class Aggregator(object):
    def __init__(self, df_source, event_handler):
        self._df_source = df_source
        self._event_handler = event_handler

    def main(self):
        interest = self._df_source.read_user_interest()
        # print(interest.head())
        timeslot = self._df_source.read_timeslot()
        # print(timeslot.head())
        min_bid = 20
        calc = BidCalculator(min_bid, interest, timeslot,
                             event_handler=self._event_handler,
                             log='.', log_level=logging.DEBUG)
        calc.main()


import signal
event_handler = None


def on_termination(signum, frame):
    global event_handler
    if event_handler is not None:
        if hasattr(event_handler, 'stop'):
            event_handler.stop()
            event_handler = None


signal.signal(signal.SIGTERM, on_termination)
signal.signal(signal.SIGINT, on_termination)

sleep_config = {
    'start': 0,
    # 'sleep': 300,
}

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='agg-config')


def get_sleep_config():
    global sleep_config
    messages = queue.receive_messages()
    if len(messages):
        last_message = messages[-1]
        if last_message is not None:
            data = json.loads(last_message.body)
            sleep_config = data
            for a_message in messages:
                a_message.delete()
            return True, sleep_config
    else:
        return False, sleep_config


def main():
    global event_handler
    import mymovie.aggregator.ddb as df_source
    from mymovie.aggregator.sqs_handler import AggregatorAsyncSqsHandler
    event_handler = AggregatorAsyncSqsHandler()
    aggregator = Aggregator(df_source, event_handler)
    while True:
        changed, _config = get_sleep_config()
        if _config['start'] == -1:
            break
        if _config['start'] > 0:
            time.sleep(_config['start'])
        aggregator.main()
        if 'sleep' in _config:
            time.sleep(_config['sleep'])
        else:
            break


    if event_handler is not None:
        event_handler.stop()
        event_handler = None


if __name__ == "__main__":
    main()



