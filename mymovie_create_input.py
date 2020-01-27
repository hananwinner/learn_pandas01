import uuid
import datetime
import numpy as np


NUM_USER = 100
user_ids = [str(uuid.uuid4())[:7] for _ in range(NUM_USER)]

titles = []
with open('titles.csv', 'r') as fdr:
    titles = fdr.readlines()

NUM_TITLE = 9
title_ids = [str(uuid.uuid4())[:7] for i in range(NUM_TITLE)]
title_dict = {id: titles[i] for i, id in enumerate(title_ids)}



BASE_TIME = datetime.datetime(year=2020, month=1, day=6).timestamp()


class EntryMaker(object):
    columns = []

    def format_header(self):
        return ','.join(self.columns) + '\n'


class UserInterestEntryMaker(EntryMaker):
    columns = ['user_id',
               # 'timestamp',
               'title_id', 'total_bid']
    user_bids = {}

    def format(self, _dict):
        # return "%s,%.2f,%s,%d\n" % \
        return "%s,%s,%d\n" % \
               (_dict['user_id'],
                # _dict['timestamp'],
                _dict['title_id'],
                _dict['total_bid'])

    def create(self, i):
        user_id = user_ids[np.random.randint(0, len(user_ids) - 1)]
        if user_id in self.user_bids:
            bid = self.user_bids[user_id]
        else:
            bid = np.random.randint(5, 100)
            self.user_bids[user_id] = bid

        return {
            'user_id': user_id,
            # 'timestamp': BASE_TIME + np.random.randint(-1000, 1000) * 1000,
            'title_id': title_ids[np.random.randint(0,len(title_dict)-1)],
            'total_bid': bid,
        }

class CreateTimeSlotEntry(EntryMaker):
    columns = ['user_id',
               # 'timestamp',
               'day']

    def create(self, i):
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
    create_file('user_interest.csv', 100, UserInterestEntryMaker())
    create_file('user_timeslot.csv', 300, CreateTimeSlotEntry())


