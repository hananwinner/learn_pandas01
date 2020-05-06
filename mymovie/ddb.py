import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
from mymovie.api.lambda_handlers.user_option import Model



def ddb_add_or_update_bid(user_id, title_id, status, num_tickets, ticket_bid,
                          _from, to, is_preapp):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-user-bids')
    table.put_item(
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
            'user_id_day': "{}_{}".format(user_id, day),
            'user_id': user_id,
            'day': day,
            'status': status,
            'is_preapp': is_preapp
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


def cancel_user_bid(user_id, title_id):
    status = Model.Bid.Status.CANCELED_BY_USER
    change_bid_status(user_id, title_id, status)


def change_bid_status(user_id, title_id, status, condition_status=None):
    dynamodb = boto3.resource('dynamodb')
    client = boto3.client('dynamodb')
    table = dynamodb.Table('test-mymovie-user-bids')
    user_id_title_id = "{}_{}".format(user_id, title_id)
    user_id_status = "{}_{}".format(user_id, status)
    condition_expr = None
    if condition_status is not None:
        condition_expr = Attr('status').eq(condition_status)
    try:
        response = table.update_item(
            Key={
                'user_id_title_id': user_id_title_id
            },
            ReturnConsumedCapacity='NONE',
            UpdateExpression="set #s = :s, user_id_status = :u_s",
            ExpressionAttributeValues={
                ':s': status,
                ':u_s': user_id_status
            },
            ExpressionAttributeNames={'#s': 'status'},
            ConditionExpression=condition_expr,
            ReturnValues='UPDATED_OLD',
        )
    except client.exceptions.ConditionalCheckFailedException as ccfx:
        return False, 'unknown'
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        err_message = 'fail to change bid\n{}\n{}\n{}\nstatus_code {}' \
            .format(user_id, title_id, status, status_code)
        print(err_message)
        raise OSError(err_message)
    else:
        is_updated = False
        old_value = 'unknown'
        if "status" in response["Attributes"]:
            is_updated = True
            old_value = response["Attributes"]["status"]
        return is_updated, old_value


def cancel_timeslot(user_id, day):
    status = Model.Bid.Status.CANCELED_BY_USER
    change_timeslot_status(user_id,day, status)


def change_timeslot_status(user_id, day, status, condition_status=None):
    dynamodb = boto3.resource('dynamodb')
    client = boto3.client('dynamodb')
    table = dynamodb.Table('test-mymovie-user-timeslots')
    user_id_day = "{}_{}".format(user_id, day)
    condition_expr = None
    if condition_status is not None:
        condition_expr = Attr('status').eq(condition_status)
    try:
        response = table.update_item(
            Key={
                'user_id_day': user_id_day
            },
            ReturnConsumedCapacity='NONE',
            UpdateExpression="set #s = :s",
            ExpressionAttributeValues={
                ':s': status,
            },
            ExpressionAttributeNames={'#s': 'status'},
            ConditionExpression=condition_expr,
            ReturnValues='UPDATED_OLD',
        )
    except client.exceptions.ConditionalCheckFailedException as ccfx:
        return False, 'unknown'
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        err_message = 'fail to change timeslot\n{}\n{}\n{}\nstatus_code {}' \
            .format(user_id, day, status, status_code)
        print(err_message)
        raise OSError(err_message)
    else:
        is_updated = False
        old_value = 'unknown'
        if "status" in response["Attributes"]:
            is_updated = True
            old_value = response["Attributes"]["status"]
        return is_updated, old_value


def fetch_timeslot_status(user_id, day):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-user-timeslots')
    user_id_day = "{}_{}".format(user_id, day)

    response = table.get_item(
        Key={
            'user_id_day': user_id_day
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


def get_timeslot_preferences(user_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-user-timeslot-preferences')
    response = table.get_item(
        Key={
            'user_id': user_id
        },
        ReturnConsumedCapacity='NONE',
    )
    if 'Item' not in response or response['Item'] is None:
        # raise ValueError("Bid for user on title not exists. user_id {} title_id {}"
        #                  .format(user_id, title_id))
        return None
    else:
        return response['Item']


def update_timeslot_preferences(user_id, is_preapp=True, or_or_any='ANY'):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-user-timeslot-preferences')
    table.put_item(Item={
        'user_id': user_id,
        'is_preapp': is_preapp,
        'or_or_any': or_or_any
        },
        ReturnValues='NONE',
        ReturnConsumedCapacity='NONE',
    )


def get_available_events():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-show-event')
    response = table.query(
        IndexName='status-index',
        Select='ALL_PROJECTED_ATTRIBUTES',
        Limit=100,
        ReturnConsumedCapacity='NONE',
        KeyConditionExpression=Key('status').eq('AVAILABLE')
    )
    return response['Items']
