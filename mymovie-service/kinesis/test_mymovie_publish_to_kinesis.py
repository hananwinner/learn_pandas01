import boto3
import base64
import json


def publish_to_kinesis(event, context):
    message = event["Records"][0]["Sns"]["Message"]

    data = {}

    data['user_id'] = message['user_id']
    data['title_id'] = message['title_id']
    data['status'] = message['status']
    data['num_tickets'] = message['num_tickets']
    data['ticket_bid'] = message['ticket_bid']
    data['from'] = message['from']
    data['to'] = message['to']
    data['is_preapp'] = message['is_preapp']

    client = boto3.client('kinesis')
    response = client.put_record(
        StreamName='test-mymovie-user-bids',
        Data=base64.b64encode(json.dumps(data)),
        PartitionKey='shard1',
    )
