import uuid
import datetime
import numpy as np
import yaml


class InputMaker(object):
    def __init__(self,
                 config_file=None, num_user=None, num_title=None):
        self._config = {}
        if config_file is not None:
            self._config = yaml.load(open(config_file, "r"))
        else:
            self._config['num_user'] = num_user
            self._config['num_title'] = num_title

        self._user_ids = [str(uuid.uuid4())[:7] for _ in
                          range(self._config['num_user'])]
        self._title_ids = [str(uuid.uuid4())[:7] for _ in
                           range(self._config['num_title'])]
        # self._BASE_TIME = base_time \
        #                   or datetime.datetime(year=2020, month=1, day=6).timestamp()

    def get_user_ids(self):
        return self._user_ids

    def get_title_ids(self):
        return self._title_ids


class EntryMaker(object):
    columns = []

    def __init__(self, db):
        self._db = db

    def format_header(self):
        return ','.join(self.columns) + '\n'


class UserInterestEntryMaker(EntryMaker):
    columns = ['user_id',
               # 'timestamp',
               'title_id', 'total_bid']
    user_bids = {}

    def __init__(self, db,
                 single_ticket_bid_low=40,
                 single_ticket_bid_high=None,
                 max_num_tickets=1):
        super(UserInterestEntryMaker, self).__init__(db)
        self._single_ticket_bid_low = single_ticket_bid_low
        self._single_ticket_bid_high = single_ticket_bid_high
        self._max_num_tickets = max_num_tickets

    def format(self, _dict):
        # return "%s,%.2f,%s,%d\n" % \
        return "%s,%s,%d\n" % \
               (_dict['user_id'],
                # _dict['timestamp'],
                _dict['title_id'],
                _dict['total_bid'])

    def create(self, i):
        user_ids = self._db.get_user_ids()
        title_ids = self._db.get_title_ids()
        user_id = user_ids[np.random.randint(0, len(user_ids) - 1)]
        if user_id in self.user_bids:
            bid = self.user_bids[user_id]
        else:
            if self._single_ticket_bid_low == self._single_ticket_bid_high and \
                    self._max_num_tickets == 1:
                bid = self._single_ticket_bid_low
            else:
                bid = \
                    np.random.randint(self._single_ticket_bid_low,
                                      self._single_ticket_bid_high) * \
                    np.random.randint(1, self._max_num_tickets)
            self.user_bids[user_id] = bid

        return {
            'user_id': user_id,
            # 'timestamp': BASE_TIME + np.random.randint(-1000, 1000) * 1000,
            'title_id': title_ids[np.random.randint(0,len(title_ids)-1)],
            'total_bid': bid,
        }

class CreateTimeSlotEntry(EntryMaker):
    columns = ['user_id',
               # 'timestamp',
               'day']

    def create(self, i):
        user_ids = self._db.get_user_ids()
        return {
            'user_id': user_ids[i % len(user_ids)],
            # 'timestamp': BASE_TIME + np.random.randint(-1000, 1000) * 1000,
            'day': datetime.datetime(year=2020, month=2, day=np.random.randint(1, 14))
        }

    def format(self, _dict):
        # return "%s,%.2f,%s\n" % \
        return "%s,%s\n" % \
               (_dict['user_id'],
                                 # _dict['timestamp'],
                             datetime.datetime.strftime(_dict['day'], '%Y/%m/%d'))


def create_file(filename, num_rows, entry_maker):
    rows = []
    for i in range(num_rows):
        row = entry_maker.create(i)
        csv_row = entry_maker.format(row)
        rows.append(csv_row)
    header = entry_maker.format_header()
    with open(filename, 'w') as fdw:
        fdw.write(header)
        fdw.writelines(rows)


if __name__ == "__main__":
    db = InputMaker(config_file='test01.yml')
    create_file('user_interest.csv', 3000, UserInterestEntryMaker(db))
    create_file('user_timeslot.csv', 9000, CreateTimeSlotEntry(db))


