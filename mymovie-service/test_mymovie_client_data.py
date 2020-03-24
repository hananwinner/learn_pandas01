import json
import boto3


def commit_client_data(event, context):
    message = event["Records"][0]["Sns"]["Message"]
    user_id = message['user_id']
    title_id = message['title_id']
    status = message['status']
    num_tickets = message['num_tickets']
    ticket_bid = message['ticket_bid']
    _from = message['from']
    to = message['to']
    is_preapp = message['is_preapp']

    client = boto3.client('dynamodb')
    client.put_item(
        TableName='test-mymovie-user-bids',
        Item={
            'user_id_title_id': {
                'S': "{}_{}".format(user_id, title_id)
            },
            'user_id': {
                'S': user_id
            },
            'title_id': {
                'S': title_id
            },
            '#s': {
                'S': status
            },
            'num_tickets': {
                'N': str(num_tickets)
            },
            'ticket_bid': {
                'N': str(ticket_bid)
            },
            '#f': {
                'S': _from
            },
            '#t': {
                'S': to
            },
            'is_preapp': {
                'BOOL': is_preapp
            },
            'user_id_status': {
                'S': "{}_{}".format(user_id, status)
            }
        },

        ReturnValues='NONE',
        ReturnConsumedCapacity='NONE',
        ExpressionAttributeNames={'#f': 'from', '#t': 'to','#s': 'status'},
    )
