import boto3
import json
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Attr, Key
from mymovie.api.lambda_handlers.common import ClientError, server_error_decorator, gen_success_response\
    , gen_client_error
from mymovie.api.lambda_handlers.common import _event_get_user_name, _event_get_bid_or_timeslot_status\
    , _event_get_is_preapp, _event_get_user_tz

from mymovie.api.lambda_handlers.user_option import Model, status_enum
from mymovie.api.lambda_handlers import ddb as db

ts_status_state_trans = {
    (None, Model.Bid.Status.AVAILABLE): (True, "Timeslot Added"),
    (None, Model.Bid.Status.CANCELED_BY_USER) : (False, "Timeslot Does Not Exists"),
    (Model.Bid.Status.AVAILABLE, Model.Bid.Status.AVAILABLE) : (True, "Timeslot Changed"),
    (Model.Bid.Status.AVAILABLE, Model.Bid.Status.CANCELED_BY_USER) : (True, "Timeslot Canceled"),
    (Model.Bid.Status.CANCELED_BY_USER, Model.Bid.Status.AVAILABLE) : (True, "Timeslot Updated"),
    (Model.Bid.Status.CANCELED_BY_USER,Model.Bid.Status.CANCELED_BY_USER) : (False, "Timeslot already Canceled"),
    (Model.Bid.Status.BOOKED,Model.Bid.Status.AVAILABLE) : (False, "Timeslot already Booked"),
    (Model.Bid.Status.BOOKED,Model.Bid.Status.CANCELED_BY_USER) : (False, "Timeslot already Booked"),
    (Model.Bid.Status.CANCELED_OTHER,Model.Bid.Status.AVAILABLE) : (False, "Timeslot already canceled by system"),
    (Model.Bid.Status.CANCELED_OTHER,Model.Bid.Status.CANCELED_BY_USER) : (False, "Timeslot already Canceled by system"),
    # time slot will not have the CANCELED_OTHER_TIMESLOT_BOOKED state
    # (Model.Bid.Status.CANCELED_OTHER_TIMESLOT_BOOKED,Model.Bid.Status.AVAILABLE) :
    #     (True, ""),
    # (Model.Bid.Status.CANCELED_OTHER_TIMESLOT_BOOKED,Model.Bid.Status.CANCELED_BY_USER) :
    #     (True, "="),
    # there is no notion of 'change' to expired timeslot - because it is represented by the date/day
    # (Model.Bid.Status.EXPIRED,Model.Bid.Status.AVAILABLE) : (True, " Updated with new dates"),
    # (Model.Bid.Status.EXPIRED,Model.Bid.Status.CANCELED_BY_USER) : (False, "Bid Already Expired and Canceled"),
}


def calc_gen_result(exist_status_or_none, new_status):
    (success, message) = ts_status_state_trans[(exist_status_or_none, new_status)]
    if success:
        return True, gen_success_response()
    else:
        return False, gen_client_error([message])


@server_error_decorator
def get_user_timeslots(event, context):
    user_id = _event_get_user_name(event)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-user-timeslots')

    possible_status_vals = \
        [status for status in status_enum if status not in ['EXPIRED']]

    response = table.query(
        IndexName='user_id',
        Select='ALL_PROJECTED_ATTRIBUTES',
        Limit=100,
        ReturnConsumedCapacity='NONE',
        FilterExpression=Attr('status').is_in(possible_status_vals),
        KeyConditionExpression=Key('user_id').eq(user_id)

    )
    return response['Items']


@server_error_decorator
def add_user_timeslot(event, context):
    user_id = _event_get_user_name(event)
    status = _event_get_bid_or_timeslot_status(event)
    if status != Model.Bid.Status.AVAILABLE:
        raise ClientError('timeslot status can only be AVAILABLE')
    user_tz = _event_get_user_tz(event)
    day = _event_get_timeslot_day(event)
    _validate_day(day, user_tz)

    exist_status = db.fetch_timeslot_status(user_id, day)
    success, result = calc_gen_result(exist_status, status)
    if success:
        is_preapp = _event_get_is_preapp(event)
        db.ddb_add_or_update_timeslot(user_id, day, user_tz, status, is_preapp)
    return json.dumps(result)


def _event_get_timeslot_day(event):
    return event['body']['show_event_date']['day']


def _validate_day(day, user_tz):
    dt_user = datetime.now(tz=user_tz)
    day_user = datetime(year=dt_user.year, month=dt_user.month, day=dt_user.day)
    input_day = datetime.strptime(day, "%Y-%m-%d")
    future_limit = day_user + timedelta(days=365)
    if input_day < day_user:
        raise ClientError("day is in the past: {}".format(day))
    elif input_day > future_limit:
        raise ClientError("day too far off in the future: {}".format(day))


@server_error_decorator
def delete_user_timeslot(event, context):
    user_id = _event_get_user_name(event)
    day = event['pathParams']['day']
    status = Model.Bid.Status.CANCELED_BY_USER
    old_status = db.fetch_timeslot_status(user_id, day)
    user_tz = _event_get_user_tz(event)

    success, result = calc_gen_result(old_status, status)
    if success:
        db.cancel_timeslot(user_id, day)
    return json.dumps(result)


@server_error_decorator
def get_user_timeslot_preferences(event, context):
    user_id = _event_get_user_name(event)
    result = db.get_timeslot_preferences(user_id)
    if result is None:
        raise ClientError("no such user")
    else:
        return json.dumps(result)


@server_error_decorator
def update_user_timeslot_preferences(event, context):
    user_id = _event_get_user_name(event)
    is_preapp = event['body']['is_preapp'] if 'is_preapp' in event['body'] else True
    or_or_any = event['body']['or_or_any'] if 'or_or_any' in event['body'] else 'ANY'
    db.update_timeslot_preferences(user_id, is_preapp, or_or_any)
