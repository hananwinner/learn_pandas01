import pytz
import traceback


SERVER_ERROR_API_GATEWAY_REGEX = "server_error"
CLIENT_ERROR_API_GATEWAY_REGEX = "client_error"


class ServerErrorException(Exception):
    def __init__(self, inner_ex):
        if inner_ex is not None:
            print(inner_ex)
        super().__init__(SERVER_ERROR_API_GATEWAY_REGEX)


class ClientError(ValueError):
    def __init__(self, msg=None):
        # _msg = CLIENT_ERROR_API_GATEWAY_REGEX
        # if msg is None:
        #     _msg = ": {}".format(msg)
        super().__init__(CLIENT_ERROR_API_GATEWAY_REGEX)


def server_error_decorator(endpoint):
    def _server_error_block(*args, **kwargs):
        try:
            return endpoint(*args, **kwargs)
        except ClientError:
            raise
        except Exception as ex:
            traceback.print_exc()
            raise ServerErrorException(ex)
    return _server_error_block


def gen_client_error(error_messages):
    return {
        "reason": "client_error",
        "errors": error_messages
    }


def gen_success_response():
    return "success"


def _event_get_title_id(event):
    return event['body']["title"]["title_id"]


def _event_get_user_name(event):
    return event['pathParams']['username']


def _event_get_bid_or_timeslot_status(event):
    return event['body']["status"] if 'status' in event['body'] else Model.Bid.Status.AVAILABLE


def _event_get_user_tz(event):
    return pytz.timezone('Asia/Jerusalem')


def _event_get_is_preapp(event):
    return event['body']['is_preapp'] if 'is_preapp' in event['body'] else True


