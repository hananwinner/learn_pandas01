from mymovie.aggregator.mymovie_create_input import SampleDB, UserInterestEntryMaker, CreateTimeSlotEntry
from mymovie.aggregator.config import Config
from mymovie.test_data_scripts.fill_titles import _clear
import boto3
from datetime import datetime, timedelta
import uuid
import random

class FillTestData(object):
    def __init__(self, config):
        self._config = config
        total_titles = config['total_titles']
        total_users = config['total_users']
        self._db = SampleDB(num_user=total_users, num_title=total_titles)

    def main(self):
        self._fill_titles()
        self._fill_users()
        self._fill_bids()
        self._fill_ts()

    def _fill_titles(self):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('test-mymovie-titles')
        _clear(table, 'title_id')
        _from = datetime.strftime(datetime.now(), "%Y-%m-%d")
        _to = datetime.strftime(datetime.now() + timedelta(days=14), "%Y-%m-%d")
        expired_to = datetime.strftime(datetime.now() - timedelta(days=1), "%Y-%m-%d")
        expired_from = datetime.strftime(datetime.now() - timedelta(days=15), "%Y-%m-%d")
        title_ids = self._db.get_title_ids()

        num_titles = self._config["total_titles"]

        with table.batch_writer() as batch:
            for i in range(num_titles):
                table.put_item(
                    Item={
                        'title_id': title_ids[i],
                        'title_name': str(uuid.uuid4())[:15],
                        'from': _from if i < num_titles / 2 else expired_from,
                        'to': _to if i < num_titles / 2 else expired_to,
                        'expired': 0 if i < num_titles / 2 else 1,
                        'year': 2020,
                        'tickets_available': 200,
                    },
                    ReturnValues='NONE',
                    ReturnConsumedCapacity='NONE',
                )

    def _fill_users(self):
        pass

    def _fill_bids(self):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('test-mymovie-user-bids')
        _clear(table, 'user_id_title_id')
        num_users = self._config["total_users"]
        bid_per_user = 2
        _from = datetime.strftime(datetime.now(), "%Y-%m-%d")
        _to = datetime.strftime(datetime.now() + timedelta(days=14), "%Y-%m-%d")
        user_ids = self._db.get_user_ids()
        title_ids = self._db.get_title_ids()
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

    def _fill_ts(self):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('test-mymovie-user-timeslots')
        _clear(table, 'user_id_day')
        ts_per_user = 2
        num_users = self._config["total_users"]
        user_ids = self._db.get_user_ids()
        with table.batch_writer() as batch:
            for i in range(num_users):
                user_id = user_ids[i]
                for j in range(ts_per_user):
                    # status = status_enum[random.randint(0, len(status_enum)-1)]
                    status = 'AVAILABLE'
                    day = datetime.strftime(datetime.now()
                                            + timedelta(days=random.randint(1, 14)),
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




if __name__ == "__main__":
    config = {
        'total_users': 100,
        'user_interset_multiplier': 0.2,
        'user_timeslot_multiplier_per_day': 0.143,
        'time_period_days': 14,
        'total_titles': 20,
        'fixed_bid': 10,
        'min_group_bid': 300,
        'test_name': 'test'
    }
    config = Config(config)
    filler = FillTestData(config)
    filler.main()
