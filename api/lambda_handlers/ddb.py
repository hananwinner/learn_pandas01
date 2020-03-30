import boto3
import json
import boto3
from datetime import datetime, timedelta
import pytz
from boto3.dynamodb.conditions import Key
from api.lambda_handlers.common import _event_get_user_tz, _event_get_is_preapp,\
    _event_get_title_id, _event_get_user_name, _event_get_bid_or_timeslot_status


def make_bid_update_message(event):
    msg = {
        "user_id": _event_get_user_name(event),
        "title_id": _event_get_title_id(event),
        "status": _event_get_bid_or_timeslot_status(event),
        "num_tickets": event['body']['ticket_bid']['num_tickets'],
        "ticket_bid": event['body']['ticket_bid']['ticket_bid'],
        "from": event['body']['from'],
        "to": event['body']['to'],
        "is_preapp": event['body']['is_preapp']
    }
    return msg


def ddb_add_or_update_bid(user_id, title_id, status, num_tickets, ticket_bid,
                          _from, to, is_preapp):
    client = boto3.client('dynamodb')
    client.put_item(
        TableName='test-mymovie-user-bids',
        Item={
            'user_id_title_id': "{}_{}".format(user_id, title_id),
            'user_id': user_id,
            'title_id': title_id,
            'status': status,
            'num_tickets': str(num_tickets),
            'ticket_bid': str(ticket_bid),
            'from': _from,
            'to': to,
            'is_preapp': is_preapp,
            'user_id_status': "{}_{}".format(user_id, status)
        },
        ReturnValues='NONE',
        ReturnConsumedCapacity='NONE',
    )


def ddb_add_or_update_timeslot(user_id, day, user_tz, status, is_preapp):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-user-timeslots')
    table.put_item(
        Item={
            'user_id': user_id,
            'day': day,
            'status': status,
            'is_preapp': is_preapp,
            'user_id_status':
                "{}_{}".format(user_id, status)
        },
        ReturnValues='NONE',
        ReturnConsumedCapacity='NONE',
    )


def fetch_bid_status(user_id, title_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-user-bids')
    response = table.get_item(
        Key={
            'user_id_title_id': "{}_{}".format(user_id,title_id)
        },
        ReturnConsumedCapacity='NONE',
        ProjectionExpression='#s',
        ExpressionAttributeNames={'#s': 'status'}
    )
    if 'Item' not in response or response['Item'] is None:
        # raise ValueError("Bid for user on title not exists. user_id {} title_id {}"
        #                  .format(user_id, title_id))
        return None
    else:
        return response['Item']['status']


def fetch_title_dates(title_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-titles')
    response = table.get_item(
        Key={
            'title_id': title_id
        },
        ReturnConsumedCapacity='NONE',
        ProjectionExpression='#f,#t',
        ExpressionAttributeNames={'#f': 'from', '#t': 'to'}
    )
    if 'Item' not in response or response['Item'] is None:
        raise ValueError("Title Id does not exists. title_id {}".format(title_id))
    else:
        return datetime.strptime(response['Item']['from'],
                                 "%Y-%m-%d"), datetime.strptime(response['Item']['to'], "%Y-%m-%d")
