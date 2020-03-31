import json
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key
from mymovie.api.lambda_handlers.common import ClientError, server_error_decorator, gen_success_response, gen_client_error
from mymovie.api.lambda_handlers.common import _event_get_user_name, _event_get_bid_or_timeslot_status, _event_get_title_id
from mymovie.api.lambda_handlers.user_option import Model
from mymovie.api.lambda_handlers import ddb as db


def validate_title_not_expired(title_id):
    _from, to = db.fetch_title_dates(title_id)
    now = datetime.now()
    if now > to or now < _from:
        raise ClientError("title is expired. title_id:{} from:{} to:{} now:{}"
                         .format(title_id, _from, to, now))

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


def calc_gen_result(exist_status_or_none, new_status):
    (success, message) = bid_status_state_trans[(exist_status_or_none, new_status)]
    if success:
        return True, gen_success_response()
    else:
        return False, gen_client_error([message])


@server_error_decorator
def get_movies(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-titles')
    response = table.query(
        IndexName='expired-index',
        Select='ALL_PROJECTED_ATTRIBUTES',
        Limit=100,
        ReturnConsumedCapacity='NONE',
        KeyConditionExpression=Key('expired').eq(0)
    )
    return response['Items']


@server_error_decorator
def get_user_active_bids(event, context):
    user_id = _event_get_user_name(event)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-user-bids')
    user_id_av = "{}_{}".format(user_id, 'AVAILABLE')
    response = table.query(
        IndexName='user_id_status',
        Select='ALL_PROJECTED_ATTRIBUTES',
        Limit=100,
        ReturnConsumedCapacity='NONE',
        KeyConditionExpression=Key('user_id_status').eq(user_id_av)
    )
    return response['Items']


@server_error_decorator
def add_or_update_user_bid(event, context):
    title_id = _event_get_title_id(event)
    username = _event_get_user_name(event)
    validate_title_not_expired(title_id)
    new_bid_status = _event_get_bid_or_timeslot_status(event)
    if new_bid_status not in [Model.Bid.Status.AVAILABLE, Model.Bid.Status.CANCELED_BY_USER]:
        return gen_client_error(["status must be AVAILABLE or CANCELED_BY_USER"])
    exist_bid_status = db.fetch_bid_status(username, title_id)
    success, result = calc_gen_result(exist_bid_status, new_bid_status)
    if success:
        db.ddb_add_or_update_bid(
            username, title_id, new_bid_status,
            event['body']['ticket_bid']['num_tickets'],
            event['body']['ticket_bid']['ticket_bid'],
            event['body']['from'], event['body']['to'],
            event['body']['is_preapp']
        )
    return json.dumps(result)


@server_error_decorator
def cancel_user_bid(event, context):
    title_id = event["pathParams"]["title_id"]
    user_id = _event_get_user_name(event)
    exist_bid_status = db.fetch_bid_status(user_id, title_id)
    new_bid_status = Model.Bid.Status.CANCELED_BY_USER
    success, result = calc_gen_result(exist_bid_status, new_bid_status)
    if success:
        db.cancel_user_bid(user_id, title_id)
    return json.dumps(result)

