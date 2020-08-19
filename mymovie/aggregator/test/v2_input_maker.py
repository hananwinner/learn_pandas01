import boto3
from datetime import datetime, timedelta
import random
from copy import copy
import uuid

TARGET_BUCKET = "fof-mymovie-agg"
TARGET_KEY = "output"

USERS_S3_OBJECT_KEY = "input/users.txt"
LOCATIONS_S3_OBJECT_KEY = "input/locations.txt"
TITLES_S3_OBJECT_KEY = "input/titles.txt"

s3 = boto3.resource('s3')

def read_user_chunk(bucket, key):
    users_object = s3.Object(bucket, key)
    response = users_object.get()
    body = response['Body']
    bytes = body.read()
    lines = bytes.decode('utf-8')
    for a_line in lines:
        parts = a_line.split(' ')
        user_id = parts[0]
        yield user_id

def make_iter(a_list):
    for x in a_list:
        yield x

def empty_gen():
    yield from ()

def parse_ids(event, ids_key, object_key, number_key):
    _ids = event.get("ids_key", None)
    _iter = None
    _num = None
    if _ids is not None:
        _iter = make_iter(_ids)
        _num = len(_ids)
    else:
        _object = event.get(object_key, None)
        if _object is not None:
            _buck, _key = _object["bucket"], _object["key"]
            if _key.endswith(".txt"):
                _iter = read_user_chunk(_buck, _key)
            else:
                # a 'directory' read chunk by chunk
                pass
        else:
            _num = event.get(number_key, None)
            if _num is None:
                raise ValueError(
                    "must specify data for the list {}, S3 object {} or just the number {}".format(
                        ids_key, object_key, number_key
                    ))
    return _iter, _num


def _make_ts_class(_from, days):
    while True:
        rand_day_inc = random.randint(0, days-1)
        rand_day_hour_inc = random.randint(0, 6) * 2
        _from_copy = copy(_from)
        _result = _from_copy + timedelta(days=rand_day_inc, hours=rand_day_hour_inc)
        yield _result


def make_circular_iter(iter):
    _list = list(iter)
    i = 0
    while True:
        i = i + 1 % len(_list)
        yield _list[i]


def convert_to_text(data):
    txt = ""
    for line in data:
        txt += line
        txt += '\n'
    return txt


def make_users_s3_object(event, context):
    num_users = event.get("num_users")
    data = []
    for _ in range(num_users):
        user_id = str(uuid.uuid4())[0:7]
        data.append(user_id)
    
    new_s3_obj = s3.Object(TARGET_BUCKET, USERS_S3_OBJECT_KEY)
    data_txt = convert_to_text(data)
    response = new_s3_obj.put(
        Body=bytes(data_txt, 'utf-8'))


def make_locations_s3_object(event, context):
    num_users = event.get("num_locations")
    data = []
    for _ in range(num_users):
        _id = str(uuid.uuid4())[0:7]
        data.append(_id)

    new_s3_obj = s3.Object(TARGET_BUCKET, LOCATIONS_S3_OBJECT_KEY)
    data_txt = convert_to_text(data)
    response = new_s3_obj.put(
        Body=bytes(data_txt, 'utf-8'))


def make_titles_s3_object(event, context):
    make_ids_s3_object(event.get("num_titles"), TITLES_S3_OBJECT_KEY)

def make_ids_s3_object(num_items, s3_key):
    data = []
    for _ in range(num_items):
        _id = str(uuid.uuid4())[0:7]
        data.append(_id)

    new_s3_obj = s3.Object(TARGET_BUCKET, s3_key)
    data_txt = convert_to_text(data)
    response = new_s3_obj.put(
        Body=bytes(data_txt, 'utf-8'))


def make_agg_input(event, context):
    """
    We create files with records that looks like this
    user_id title_id timeslot location_id total_bid
    u1 t1 ts1 loc1 12
    :param event:
    :param context:
    :return:
    """
    bids_per_user = event.get("bids_per_user")
    ts_per_user = event.get("ts_per_user")
    loc_per_user = event.get("loc_per_user")
    output_with_user_id = event.get("with_user_id", False)

    user_iter, num_users = parse_ids(event, "user_ids", "users_s3_object", "num_users")
    loc_iter, num_locations = parse_ids(event, "loc_ids", "locations_s3_object", "num_locations")
    title_iter, num_titles = parse_ids(event, "title_ids", "titles_s3_object", "num_titles")

    rand_ts_iter = prepare_rand_ts_iter(event)

    title_circ_iter = make_circular_iter(title_iter)
    loc_circ_iter = make_circular_iter(loc_iter)

    postfix = str(uuid.uuid4())[0:7]
    postfix = '/'.join(TARGET_KEY, postfix)
    file_index = 0
    data = []
    line_count = 0
    for a_user in user_iter:
        total_bid = random.randint(10, 15) * random.randint(1, 4)
        for _ in range(bids_per_user):
            a_title_id = title_circ_iter.__next__()
            for _ in range(ts_per_user):
                a_ts = rand_ts_iter.__next__()
                for _ in range(loc_per_user):
                    a_loc = loc_circ_iter.__next__()
                    if output_with_user_id:
                        line = "%s %s %s %s %d" % \
                        a_user, a_title_id, datetime.strftime(a_ts, "%Y-%m-%d %H:00"), a_loc, total_bid
                    else:
                        line = "%s %s %s %d" % \
                               a_title_id, datetime.strftime(a_ts, "%Y-%m-%d %H:00"), a_loc, total_bid
                    line_count += 1
                    data.append(line)
                    data, line_count = check_emit_file(data, file_index, line_count, postfix)


def prepare_rand_ts_iter(event):
    _from = event.get("timeslots_from", None)
    if _from is None:
        _from = datetime.now()
    days = event.get("timeslots_period_days", 14)
    rand_ts_iter = _make_ts_class(_from, days)
    return rand_ts_iter


def check_emit_file(data, file_index, line_count, postfix):
    if line_count >= 10000:
        emit_file(data, file_index, postfix)
        file_index += 1
        data = []
        line_count = 0
    return data, line_count


def emit_file(data, file_index, postfix):
    data_txt = convert_to_text(data)
    target_file = '/'.join(postfix, str(file_index).zfill(2))
    new_s3_obj = s3.Object(TARGET_BUCKET, target_file)
    response = new_s3_obj.put(
        Body=bytes(data_txt))


if __name__ == "__main__":
    # event = {
    #     "num_users": 10
    # }
    # make_users_s3_object(event, None)

    # event = {
    #     "num_locations": 10
    # }
    # make_locations_s3_object(event, None)

    # event = {
    #     "num_titles": 10
    # }
    # make_titles_s3_object(event, None)

    event = {
        "with_user_id": True,
        "bids_per_user": 2,
        "ts_per_user": 2,
        "loc_per_user": 5,
        "users_s3_object": {
            "bucket": TARGET_BUCKET,
            "key": USERS_S3_OBJECT_KEY
        },
        "locations_s3_object": {
            "bucket": TARGET_BUCKET,
            "key": LOCATIONS_S3_OBJECT_KEY
        },
        "titles_s3_object": {
            "bucket": TARGET_BUCKET,
            "key": TITLES_S3_OBJECT_KEY
        }

    }
    make_agg_input(event, None)















