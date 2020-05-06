import boto3
from mymovie.apply.simple_handler import SimpleSqsToDynDbHandler
from mymovie import ddb as db


class NewReservationConsumer(SimpleSqsToDynDbHandler):
    def __init__(self):
        super().__init__('test-mymovie-apply-new-reservation', 'test-mymovie-user-bookings')
        dynamodb = boto3.resource('dynamodb')
        self._titles_table = dynamodb.Table('test-mymovie-titles')
        self._bids_table = dynamodb.Table('test-mymovie-user-bids')

    def fetch_show_details(self, title_id):
        response = self._titles_table.get_item(
            Key={
                'title_id': title_id
            })
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
        response = self._bids_table.get_item(
            Key={
                'user_id_title_id': user_id_title_id
            })
        if 'Item' not in response:
            raise ValueError("no such bid")
        else:
            item = response['Item']
            is_preapp, num_tickets, ticket_bid = \
                item['is_preapp'], item['num_tickets'], item['ticket_bid']
            return is_preapp, num_tickets, ticket_bid

    def _try_make_item(self, data):
        user_id = data['user_id']
        day = data['day']
        title_id = data['title_id']
        name, year, _from, _to, _ = self.fetch_show_details(title_id)
        is_preapp, num_tickets, ticket_bid = self.fetch_bid_details(user_id, title_id)
        status = 'BOOKED'
        if not self._book_bid(user_id, title_id):
            return None
        if not self._book_timeslot(user_id, day):
            return None
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
        is_updated, _ = db.change_bid_status(user_id, title_id, "BOOKED", condition_status="AVAILABLE")
        return is_updated


    def _book_timeslot(self, user_id, day):
        is_updated, _ = db.change_timeslot_status(user_id, day, "BOOKED", condition_status="AVAILABLE")
        return is_updated

def main():
    NewReservationConsumer().main()


if __name__ == "__main__":
    main()
