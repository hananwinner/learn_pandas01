import pandas as pd
import datetime
import time


def parse_day(day_str):
    return datetime.datetime.strptime(day_str, "%Y/%m/%d")

def read_timeslot():
    df = pd.read_csv('user_timeslot.csv', index_col=['user_id'],
                      dtype={'user_id': 'object', 'timestamp': 'float64',
                             'day': 'object'})
    # print(df)
    # max_index = df.groupby(['user_id','timestamp'])["timestamp"].max()
    # df.loc(max_index)
    df['day'] = df["day"].apply(parse_day)
    # df = df.set_index('user_id')
    return df

def read_user_interest():
    df = pd.read_csv('user_interest.csv', index_col=['user_id'],
                      dtype={'user_id': 'object', 'timestamp': 'float64',
                             'title_id': 'object', 'total_bid': 'int64'})
    return df


def read_timeslot2():
    df2 = pd.read_csv('user_timeslot.csv', index_col=None,
                      parse_dates=['day'], date_parser=parse_day,
                      dtype={'user_id': 'object', 'timestamp': 'float64',
                             })

if __name__ == "__main__":
    # df = pd.read_csv('user_interest.csv', index_col='user_id',
    #                  dtype={'user_id': 'object', 'timestamp': 'float64',
    #                         'title_id': 'object', 'total_bid': 'int64'})

    tic = time.time()
    df = read_timeslot()
    toc = time.time()
    print('read_timeslot elapsed:',toc-tic)
    tic = time.time()
    df2 = read_user_interest()
    toc = time.time()
    print('read_user_interest elapsed:', toc - tic)

    df = pd.merge(df, df2, on=['user_id'])
    print(df)








