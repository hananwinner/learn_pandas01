import pandas as pd
import numpy as np
import datetime
import pytz


utc = pytz.utc
est = pytz.timezone('US/Eastern')


def date_parse(date_str):
    dt = datetime.datetime.strptime(date_str, "%Y/%m/%d %H:%M")
    dt = utc.localize(dt)
    dt = dt.astimezone(est).replace(tzinfo=None)
    return dt


def alter_indexes(df):
    df = df.set_index(["camp_id", "date"])
    return df


df = pd.read_csv('cost.csv', index_col=None,
                 parse_dates=True,
                 date_parser=date_parse,
                 dtype={'camp_id':'object', 'clicks':'int64',
                        'cost':'float64'})
print(df)
df = alter_indexes(df)

df_rev = pd.read_csv('rev.csv', index_col=None,
                     parse_dates=True,
                     date_parser=date_parse,
                     dtype={'camp_id': 'object', 'rev': 'float64'})
df_rev = alter_indexes(df_rev)
# print(df_rev)

# print(df)
# print

# print(df_rev.columns)
# print(df.columns)

df = pd.merge(df,df_rev, on=['camp_id', 'date'])

df["profit"] = df["rev"] - df["cost"]
df["profit_hour"] = df["profit"] > 0

def index_day_part(entry):
    camp_id, date = entry
    date = datetime.datetime.strptime(date, "%Y/%m/%d %H:%M")
    date_minus_time = datetime.datetime(year=date.year, month=date.month, day=date.day)
    return camp_id, date_minus_time

df_sum = df.groupby(by=index_day_part).sum()


print(df_sum)



