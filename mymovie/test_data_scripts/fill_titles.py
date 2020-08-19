import boto3
import uuid
from datetime import datetime, timedelta
import random


def _clear(table, index_name):
    '''
    clears all items

    :param table: DynamoDB table name
    :param index_name: primary index name
    :return: None

    '''
    scan = table.scan(
        ProjectionExpression=index_name
    )

    with table.batch_writer() as batch:
        for each in scan['Items']:
            batch.delete_item(Key=each)


def fill_users(event, context):
    '''
    fill random users from the 'user_ids' list
    :param event: dict with:
    'user_ids'
    :param context:
    :return:
    '''
    dynamodb= boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-users')

    clear = event['clear'] if 'clear' in event else True
    just_clear = event['just_clear'] if 'just_clear' in event else False
    if clear or just_clear:
        _clear(table, 'user_id')
    if just_clear:
        return

    user_ids = event['user_ids']
    for id in user_ids:
        table.put_item(
            Item={
                'user_id': id,
            },
            ReturnValues='NONE',
            ReturnConsumedCapacity='NONE',
        )


def fill_titles(event, context):
    '''
    fills the titles table with titles with ids as specified,
    and random availabilty range between the specified limits,
    and each other movie is on expired dates

    :param event:
    'title_ids' - a list of title_ids to fill into the table
    'from', 'to': specify range of dates within the the movies are available to watch
    :param context:
    :return:
    '''
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
                    'expired': 0 if i < num_titles/2 else 1,
                    'year': 2020,
                    'tickets_available': 200,
                },
                ReturnValues='NONE',
                ReturnConsumedCapacity='NONE',
            )


def fill_bids(event, context):
    '''
    create bids on titles by users
    at specified range, all 'AVAILABLE'
    :param event:
    'user_ids' - a list of user ids to fill into the table
    'title_ids' - a list of title ids to fill into the table
    'bid_per_user': default 2
    :param context:
    :return:
    '''
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
                        'num_tickets': 1,
                        'ticket_bid': 10,
                        'from': _from,
                        'to': _to,
                        'is_preapp': True,
                        'user_id_status': "{}_{}".format(user_id, 'AVAILABLE')
                    },
                    ReturnValues='NONE',
                    ReturnConsumedCapacity='NONE',
                )


def fill_timeslots(event, context):
    '''
    create timeslots for users on specified range, all AVAILABLE
    :param event:
    ts_per_user - deaf. 2
    user_ids
    :param context:
    :return:
    '''
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-user-timeslots')

    clear = event['clear'] if 'clear' in event else True
    just_clear = event['just_clear'] if 'just_clear' in event else False

    if clear or just_clear:
        _clear(table, 'user_id_day')
    if just_clear:
        return

    if 'user_ids' in event:
        user_ids = event['user_ids']
        num_users = len(user_ids)
    else:
        num_users = event['num_users'] if 'num_users' in event else 50
        user_ids = [str(uuid.uuid4())[:7] for _ in range(num_users)]

    ts_per_user = event['ts_per_user'] if 'ts_per_user' in event else 2

    # _from = datetime.strftime(datetime.now(), "%Y-%m-%d")
    # _to = datetime.strftime(datetime.now() + timedelta(days=14), "%Y-%m-%d")
    # if 'from' in event:
    #     _from = event['from']
    # if 'to' in event:
    #     _to = event['to']

    status_enum = \
        ['AVAILABLE', 'EXPIRED']
        # ['AVAILABLE', 'BOOKED', 'CANCELED_BY_USER', 'CANCELED_OTHER_TIMESLOT_BOOKED', 'CANCELED_OTHER', 'EXPIRED' ]

    with table.batch_writer() as batch:
        for i in range(num_users):
            user_id = user_ids[i]
            for j in range(ts_per_user):
                # status = status_enum[random.randint(0, len(status_enum)-1)]
                status = 'AVAILABLE'
                day = datetime.strftime(datetime.now() + timedelta(days=random.randint(1, 14)),
                                                   "%Y-%m-%d")
                table.put_item(
                    Item={
                        'user_id_day': "{}_{}".format(user_id, day),
                        'user_id': user_id,
                        'day': day,
                        'status': status,
                        'is_preapp': True},
                    ReturnValues='NONE',
                    ReturnConsumedCapacity='NONE',
                )

def fill_shows(event, context):
    '''
    fill shows of movies
    :param event:
    :param context:
    :return:
    '''
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-show-event')

    clear = event['clear'] if 'clear' in event else True
    just_clear = event['just_clear'] if 'just_clear' in event else False

    if clear or just_clear:
        _clear(table, 'user_id_day')
    if just_clear:
        return
    title_ids = event['title_ids']


    title_id_day = '{}_{}'.format(title_id, day)
    item = {
        'title_id_day': title_id_day,
        'titld_id': title_id,
        'title_name': name,
        'from': _from,
        'to': _to,
        'year': '' if year is None else year,
        'day': day,
        'status': status,
        'num_tickets_available': num_tickets_remain,
        'ticket_price': offer_price,
    }
