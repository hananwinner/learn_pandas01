import json
from mymovie import ddb as db
from mymovie.api.lambda_handlers.common import server_error_decorator
from mymovie.api.lambda_handlers.common import _event_get_user_name


@server_error_decorator
def get_show_events(event, context):
    return json.dumps(db.get_available_events())


@server_error_decorator
def buy_user_ticket(event, context):
    event_id = event['pathParams']['event_id']
    user_id = _event_get_user_name(event)

    # make a bid which is booked
    # what if I had a bid on that date? override it. unless canceled-other

    raise NotImplementedError()

@server_error_decorator
def get_user_bookings(event, context):
    raise NotImplementedError()


def delete_user_booking(event, context):
    raise NotImplementedError()