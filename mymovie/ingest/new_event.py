import boto3
import json
import uuid
import math


dynamodb = boto3.resource('dynamodb')
events_table = dynamodb.Table('test-mymovie-show-event')
shows_table = dynamodb.Table('test-mymovie-titles')

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='new_reservation')


def poll_new_events():
    messages = queue.receive_messages(
        MaxNumberOfMessages=10,
    )
    return messages


def get_data_dict(message):
    return json.loads(message["Body"])


def fetch_show_details(title_id):
    response = shows_table.get_item(title_id)
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


def delete_message(message):
    message.delete()


def main_new_event():
    while True:
        messages = poll_new_events()
        for a_message in messages:
            data = get_data_dict(a_message)
            title_id = data['title_id']
            day = data['day']
            num_tickets = data['num_tickets']
            bids_total = data['bids_total']
            try:
                name, year, _from, _to, tickets_available = fetch_show_details(title_id)
            except ValueError:
                delete_message(a_message)
                continue

            status = 'AVAILABLE'
            num_tickets_remain = tickets_available - num_tickets
            if num_tickets_remain <= 0:
                status = 'FULL'

            avg_price = bids_total / num_tickets
            avg_price *= 1.25
            offered_price = math.ceil(avg_price)

            event_id = str(uuid.uuid4()[:7])
            events_table.put_item(
                Item={
                    'show_event_id': event_id,
                    'titld_id': title_id,
                    'title_name': name,
                    'from' : _from,
                    'to': _to,
                    'year': '' if year is None else year,
                    'day': day,
                    'status': status,
                    'num_tickets_available': num_tickets_remain,
                    

                }
            )



