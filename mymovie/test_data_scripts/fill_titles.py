import boto3
import uuid
from datetime import datetime, timedelta
import random


def _clear(table, index_name):
    scan = table.scan(
        ProjectionExpression=index_name
    )

    with table.batch_writer() as batch:
        for each in scan['Items']:
            batch.delete_item(Key=each)


def fill_titles(event, context):

    num_titles = event['num_titles'] if 'num_titles' in event else 100
    clear = event['clear'] if 'clear' in event else True
    just_clear = event['just_clear'] if 'just_clear' in event else False


    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-titles')

    if clear or just_clear:
        _clear(table, 'title_id')

    if just_clear:
        return

    _from = datetime.strftime(datetime.now(), "%Y-%m-%d")
    _to = datetime.strftime(datetime.now() + timedelta(days=14), "%Y-%m-%d")
    if 'from' in event:
        _from = event['from']
    if 'to' in event:
        _to = event['to']

    if 'title_ids' in event:
        title_ids = event['title_ids']
        num_titles = len(title_ids)
    else:
        title_ids = [str(uuid.uuid4())[:7] for _ in range(num_titles)]

    expired_to = datetime.strftime(datetime.now() - timedelta(days=1), "%Y-%m-%d")
    expired_from = datetime.strftime(datetime.now() - timedelta(days=15), "%Y-%m-%d")

    with table.batch_writer() as batch:
        for i in range(num_titles):
            table.put_item(
                Item={
                    'title_id': title_ids[i],
                    'title_name': str(uuid.uuid4())[:15],
                    'from': _from if i < num_titles/2 else expired_from,
                    'to': _to if i < num_titles/2 else expired_to,
                    'expired': 0 if i < num_titles/2 else 1
                },
                ReturnValues='NONE',
                ReturnConsumedCapacity='NONE',
            )


def fill_bids(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-user-bids')

    clear = event['clear'] if 'clear' in event else True
    just_clear = event['just_clear'] if 'just_clear' in event else False
    if clear or just_clear:
        _clear(table, 'user_id_title_id')
    if just_clear:
        return

    bid_per_user = event['bid_per_user'] if 'bid_per_user' in event else 2

    _from = datetime.strftime(datetime.now(), "%Y-%m-%d")
    _to = datetime.strftime(datetime.now() + timedelta(days=14), "%Y-%m-%d")
    if 'from' in event:
        _from = event['from']
    if 'to' in event:
        _to = event['to']

    if 'title_ids' in event:
        title_ids = event['title_ids']
        num_av_titles = len(title_ids)
    else:
        num_av_titles = 10
        title_ids = [str(uuid.uuid4())[:7] for _ in range(num_av_titles)]

    if 'user_ids' in event:
        user_ids = event['user_ids']
        num_users = len(user_ids)
    else:
        num_users = event['num_users'] if 'num_users' in event else 100
        user_ids = [str(uuid.uuid4())[:7] for _ in range(num_users)]

    with table.batch_writer() as batch:
        for i in range(num_users):
            user_id = user_ids[i]
            for j in range(bid_per_user):
                title_id = title_ids[j % len(title_ids)]
                table.put_item(
                    Item={
                        'user_id_title_id': "{}_{}".format(user_id, title_id),
                        'user_id': user_id,
                        'title_id': title_id,
                        'status': 'AVAILABLE',
                        'num_tickets': '1',
                        'ticket_bid': '10',
                        'from': _from,
                        'to': _to,
                        'is_preapp': True,
                        'user_id_status': "{}_{}".format(user_id, 'AVAILABLE')
                    },
                    ReturnValues='NONE',
                    ReturnConsumedCapacity='NONE',
                )


def fill_timeslots(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-user-timeslots')

    clear = event['clear'] if 'clear' in event else True
    just_clear = event['just_clear'] if 'just_clear' in event else False

    if clear or just_clear:
        _clear(table, 'user_id')
    if just_clear:
        return

    if 'user_ids' in event:
        user_ids = event['user_ids']
        num_users = len(user_ids)
    else:
        num_users = event['num_users'] if 'num_users' in event else 50
        user_ids = [str(uuid.uuid4())[:7] for _ in range(num_users)]

    ts_per_user = event['ts_per_user'] if 'ts_per_user' in event else 2

    _from = datetime.strftime(datetime.now(), "%Y-%m-%d")
    _to = datetime.strftime(datetime.now() + timedelta(days=14), "%Y-%m-%d")
    if 'from' in event:
        _from = event['from']
    if 'to' in event:
        _to = event['to']

    status_enum = \
        ['AVAILABLE', 'EXPIRED']
        # ['AVAILABLE', 'BOOKED', 'CANCELED_BY_USER', 'CANCELED_OTHER_TIMESLOT_BOOKED', 'CANCELED_OTHER', 'EXPIRED' ]

    with table.batch_writer() as batch:
        for i in range(num_users):
            user_id = user_ids[i]
            for j in range(ts_per_user):
                status = status_enum[random.randint(0, len(status_enum)-1)]
                day = datetime.strftime(datetime.now() + timedelta(days=random.randint(1, 14)),
                                                   "%Y-%m-%d")
                table.put_item(
                    Item={
                        'user_id_day': "{}_{}".format(user_id, day),
                        'user_id': user_id,
                        'day': day,
                        'status': status,
                        'is_preapp': True,
                        'user_id_status':
                            "{}_{}".format(user_id, status)
                    },
                    ReturnValues='NONE',
                    ReturnConsumedCapacity='NONE',
                )
