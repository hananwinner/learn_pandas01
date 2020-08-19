import boto3
import json

sqs = boto3.resource('sqs')
sqs_queue = sqs.get_queue_by_name(QueueName='test-mymovie-apply-new-reservation')

def send(message):
    response = sqs_queue.send_message(
        MessageBody=json.dumps(message),
    )
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        print('message status code {}\n{}'.format(status_code, message))
        return False
    else:
        return True


def generate_show_message(title_id, day, num_tickets):
    '''
    'title_id':
            'day': day,
            'num_tickets': 200
            'bids_total': default num_tickets*10
    :param title_id:
    :param day:
    :return:
    '''



def generate_message(i):
    '''
    generate a booking message
    'user_id': random user_id
    'day': a day within range of 'to' and 'from' - default
        is today and two weeks from now
    'title_id': random title_id

    to be able to handle the booking, need that 'show' exists
    '''

def publish_new_reservations():
    for i in range(2500):
        message = generate_message(i)
        send(message)


if __name__ == "__main__":
    publish_new_reservations()