import boto3
import math
from mymovie.ingest.simple_handler import SimpleSqsToDynDbHandler

class NewReservationConsumer(SimpleSqsToDynDbHandler):
    def __init__(self):
        super().__init__('new_reservation', 'test-mymovie-user-bookings')
        dynamodb = boto3.resource('dynamodb')
        self._titles_table = dynamodb.Table('test-mymovie-titles')
        self._bids_table = dynamodb.Table('test-mymovie-user-bids')

    def fetch_show_details(self, title_id):
        response = self._titles_table.get_item(title_id)
        if 'Item' not in response:
            raise ValueError("no such show")
        else:
            item = response['Item']
            name = item['title_name']
            year = item['year'] if 'year' in item else None
            _from = item['from']
            _to = item['to']
            tickets_available = item['tickets_available']
            return name, year, _from, _to, tickets_available

    def fetch_bid_details(self, user_id, title_id):
        user_id_title_id = "{}_{}".format(user_id, title_id)
        response = self._bids_table.get_item(user_id_title_id)
        if 'Item' not in response:
            raise ValueError("no such bid")
        else:
            item = response['Item']
            is_preapp, num_tickets, ticket_bid = \
                item['is_preapp'], item['num_tickets'], item['ticket_bid']
            return is_preapp, num_tickets, ticket_bid

    def try_make_item(self, data):
        user_id = data['user_id']
        day = data['day']
        title_id = data['title_id']
        name, year, _from, _to, _ = self.fetch_show_details(title_id)
        is_preapp, num_tickets, ticket_bid = self.fetch_bid_details(user_id, title_id)
        status = 'BOOKED'
        self._book_bid(user_id, title_id)
        event_id = '{}_{}'.format(title_id, day)
        user_id_event_id = '{}_{}'.format(user_id, event_id)
        item = {
            'user_id_event_id': user_id_event_id,
            'status': status,
            'is_preapp': is_preapp,
            'num_tickets': num_tickets,
            'ticket_bid': ticket_bid,
            'user_id': user_id,
            'day': day,
            'title_id': title_id,
            'event_id': event_id,
            'title_name': name,
            'title_year': year,
        }
        return item

    def _book_bid(self, user_id, title_id):
        user_id_title_id = "{}_{}".format(user_id, title_id)
        status = "BOOKED"
        user_id_status = "{}_{}".format(user_id, status)
        response = self._bids_table.update_item(
            Key={
                'user_id_title_id': user_id_title_id
            },
            ReturnConsumedCapacity='NONE',
            UpdateExpression="set #s = :s, user_id_status = :u_s",
            ExpressionAttributeValues={
                ':s': status,
                ':u_s': user_id_status
            },
            ExpressionAttributeNames={'#s': 'status'}
        )
        status_code = response['ResponseMetadata']['HTTPStatusCode']
        if status_code != 200:
            err_message = 'fail to book bid user_id_title_id {} HTTPStatusCode {}'\
                .format(user_id_title_id, status_code)
            print(err_message)
            raise OSError(err_message)


def main():
    NewReservationConsumer().main()


if __name__ == "__main__":
    main()
