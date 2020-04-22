import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key
from mymovie.api.lambda_handlers.user_option import Model
import pandas as pd


def parse_day(day_str):
    return datetime.strptime(day_str, "%Y-%m-%d")


def read_user_interest():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-user-bids')

    response = table.scan(
        FilterExpression=Key('status').eq(Model.Bid.Status.AVAILABLE),
        Select="SPECIFIC_ATTRIBUTES",
        ProjectionExpression='user_id,title_id,num_tickets,ticket_bid'
    )
    items = []
    if 'Items' in response:
        items = response['Items']

    df = pd.DataFrame(items, columns=['user_id', 'title_id', 'num_tickets', 'ticket_bid'])
    df['total_bid'] = df['num_tickets']*df['ticket_bid']
    df = df.loc[:,['user_id', 'title_id','total_bid']]
    df = df.set_index(keys=['user_id'])
    return df


def read_timeslot():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-user-timeslots')

    response = table.scan(
        FilterExpression=Key('status').eq(Model.Bid.Status.AVAILABLE),
        Select="SPECIFIC_ATTRIBUTES",
        ProjectionExpression='user_id,#d',
        ExpressionAttributeNames = {'#d': 'day'}
    )

    items = []
    if 'Items' in response:
        items = response['Items']

    df = pd.DataFrame(items, columns=['user_id', 'day'])
    df['day'] = df["day"].apply(parse_day)
    df = df.set_index(keys=['user_id'])
    return df


if __name__ == "__main__":
    df = read_timeslot()
