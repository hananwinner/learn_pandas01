import json
import boto3
from datetime import datetime


class Model:
    class Bid:
        class Status:
            AVAILABLE = "AVAILABLE"
            CANCELED_BY_USER = "CANCELED_BY_USER"
            BOOKED = "BOOKED"
            CANCELED_OTHER_TIMESLOT_BOOKED = "CANCELED_OTHER_TIMESLOT_BOOKED"
            CANCELED_OTHER = "CANCELED_OTHER"
            EXPIRED = "EXPIRED"


class Topic:
    BID_UPDATED = "BID_UPDATED"


def get_title_id(event):
    return event['body']["title"]["_id"]


def get_user_name(event):
    return event['pathParams']['username']


def get_bid_status(event):
    return event['body']["status"] if 'status' in event['body'] else Model.Bid.Status.AVAILABLE


def gen_client_error(error_messages):
    return {
        "reason": "client_error",
        "errors": error_messages
    }


def gen_success(payload=None, messages=None):
    return "success"


def validate_title_not_expired(title_id):
    _from, to = fetch_title_dates(title_id)
    now = datetime.now()
    if now > to or now < _from:
        raise ValueError("title is expired. title_id:{} from:{} to:{} now:{}"
                         .format(title_id, _from, to, now))


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


def send_sns(topic, payload):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:eu-west-1:987471261617:topic-test-mymovie-client_data')
    response = topic.publish(Message=json.dumps(payload))


def make_bid_update_message(event):
    msg = {
        "user_id": get_user_name(event),
        "title_id": get_title_id(event),
        "status": get_bid_status(event),
        "num_tickets": event['body']['ticket_bid']['num_tickets'],
        "ticket_bid": event['body']['ticket_bid']['ticket_bid'],
        "from": event['body']['from'],
        "to": event['body']['to'],
        "is_preapp": event['body']['is_preapp']
    }
    return msg

bid_status_state_trans = {
    (None,Model.Bid.Status.AVAILABLE) : (True, "Bid Updated"),
    (None,Model.Bid.Status.CANCELED_BY_USER) : (False, "Bid Does Not Exists"),
    (Model.Bid.Status.AVAILABLE,Model.Bid.Status.AVAILABLE) : (True, "Bid Changed"),
    (Model.Bid.Status.AVAILABLE,Model.Bid.Status.CANCELED_BY_USER) : (True, "Bid Canceled"),
    (Model.Bid.Status.CANCELED_BY_USER,Model.Bid.Status.AVAILABLE) : (True, "Bid Updated"),
    (Model.Bid.Status.CANCELED_BY_USER,Model.Bid.Status.CANCELED_BY_USER) : (False, "Bid already Canceled"),
    (Model.Bid.Status.BOOKED,Model.Bid.Status.AVAILABLE) : (False, "Bid already Booked"),
    (Model.Bid.Status.BOOKED,Model.Bid.Status.CANCELED_BY_USER) : (False, "Bid already Booked"),
    (Model.Bid.Status.CANCELED_OTHER,Model.Bid.Status.AVAILABLE) : (False, "Bid already canceled by system"),
    (Model.Bid.Status.CANCELED_OTHER,Model.Bid.Status.CANCELED_BY_USER) : (False, "Bid already Canceled by system"),
    (Model.Bid.Status.CANCELED_OTHER_TIMESLOT_BOOKED,Model.Bid.Status.AVAILABLE) : (True, "Bid updated but check if time-slots are available"),
    (Model.Bid.Status.CANCELED_OTHER_TIMESLOT_BOOKED,Model.Bid.Status.CANCELED_BY_USER) :
        (True, "Bid canceled (note there appears to be no  time-slots available anyway"),
    (Model.Bid.Status.EXPIRED,Model.Bid.Status.AVAILABLE) : (True, "Bid Updated with new dates"),
    (Model.Bid.Status.EXPIRED,Model.Bid.Status.CANCELED_BY_USER) : (False, "Bid Already Expired and Canceled"),
}


def calc_gen_result(exist_status_or_none, new_status, payload=None):
    (success, message) = bid_status_state_trans[(exist_status_or_none, new_status)]
    if success:
        return True, gen_success([message], payload)
    else:
        return False, gen_client_error([message])


def get_movies(event, context):
    return {
        'statusCode': 200,
        'body': 'body'
    }


def get_user_active_bids(event, context):
    return {
        'statusCode': 200,
        'body': 'body'
    }


def add_or_update_user_bid(event, context):
    title_id = get_title_id(event)
    username = get_user_name(event)
    validate_title_not_expired(title_id)

    new_bid_status = get_bid_status(event)
    if new_bid_status not in [Model.Bid.Status.AVAILABLE, Model.Bid.Status.CANCELED_BY_USER]:
        return gen_client_error(["status must be AVAILABLE or CANCELED_BY_USER"])

    exist_bid_status = fetch_bid_status(username, title_id)

    payload = make_bid_update_message(event)
    success, result = calc_gen_result(exist_bid_status, new_bid_status,payload)
    if success:
        send_sns(Topic.BID_UPDATED, payload)
    return json.dumps(result)


def cancel_user_bid(event, context):
    title_id = get_title_id(event)
    username = get_user_name(event)

    exist_bid_status = fetch_bid_status(username, title_id)

    new_bid_status = Model.Bid.Status.CANCELED_BY_USER

    payload = make_bid_update_message(event)
    success, result = calc_gen_result(exist_bid_status, new_bid_status, payload)
    if success:
        send_sns(Topic.BID_UPDATED, payload)
    return json.dumps(result)


def get_user_timeslots(event, context):
    return {
        'statusCode': 200,
        'body': 'body'
    }


def delete_user_timeslots(event, context):
    return {
        'statusCode': 200,
        'body': 'body'
    }


def add_or_update_user_timeslots(event, context):
    return {
        'statusCode': 200,
        'body': 'body'
    }


def add_user_timeslot(event, context):
    return {
        'statusCode': 200,
        'body': 'body'
    }


def delete_user_timeslot(event, context):
    return {
        'statusCode': 200,
        'body': 'body'
    }


def get_user_timeslot_preferences(event, context):
    return {
        'statusCode': 200,
        'body': 'body'
    }


def update_user_timeslot_preferences(event, context):
    return {
        'statusCode': 200,
        'body': 'body'
    }


def get_show_events(event, context):
    return {
        'statusCode': 200,
        'body': 'body'
    }


def buy_user_ticket(event, context):
    return {
        'statusCode': 200,
        'body': 'body'
    }


def get_user_bookings(event, context):
    return {
        'statusCode': 200,
        'body': 'body'
    }


def delete_user_booking(event, context):
    return {
        'statusCode': 200,
        'body': 'body'
    }
