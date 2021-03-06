import boto3
import math
from mymovie.apply.simple_handler import SimpleSqsToDynDbHandler


class NewEventConsumer(SimpleSqsToDynDbHandler):
    def __init__(self):
        super().__init__('test-mymovie-apply-new-event', 'test-mymovie-show-event')
        dynamodb = boto3.resource('dynamodb')
        self._titles_table = dynamodb.Table('test-mymovie-titles')

    def _fetch_show_details(self, title_id):
        response = self._titles_table.get_item(
            Key={
                'title_id': title_id
            })
        if 'Item' not in response:
            raise ValueError("no such title")
        else:
            item = response['Item']
            name = item['title_name']
            year = item['year'] if 'year' in item else None
            _from = item['from']
            _to = item['to']
            return name, year, _from, _to

    def _try_make_item(self, data):
        '''
        gets the title data and creates an event record
        :param data:
        :return:
        '''
        title_id = data['title_id']
        day = data['day']
        num_tickets = data['num_tickets']
        bids_total = data['bids_total']
        name, year, _from, _to = self._fetch_show_details(title_id)
        status = 'AVAILABLE'
        num_tickets_remain = 200 - num_tickets
        if num_tickets_remain <= 0:
            status = 'FULL'

        avg_price = bids_total / num_tickets
        avg_price *= 1.25
        offer_price = math.ceil(avg_price)

        # event_id = str(uuid.uuid4()[:7])
        title_id_day = '{}_{}'.format(title_id, day)
        item = {
            'title_id_day': title_id_day,
            'titld_id': title_id,
            'title_name': name,
            'from': _from,
            'to': _to,
            'year': '' if year is None else year,
            'day': day,
            'status': status,
            'num_tickets_available': num_tickets_remain,
            'ticket_price': offer_price,
        }
        return item


def main():
    NewEventConsumer().main()


if __name__ == "__main__":
    main()
