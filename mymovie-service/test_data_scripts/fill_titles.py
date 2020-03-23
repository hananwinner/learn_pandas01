import boto3
import uuid
from datetime import datetime, timedelta


def fill_titles(event, context):

    num_titles = event['num_titles'] if 'num_titles' in event else 100
    clear = event['clear'] if 'clear' in event else True

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test-mymovie-titles-v2')

    if clear:
        scan = table.scan(
            ProjectionExpression='title_id'
        )

        with table.batch_writer() as batch:
            for each in scan['Items']:
                batch.delete_item(Key=each)

    _from = datetime.strftime(datetime.now(), "%Y-%m-%d")
    _to = datetime.strftime(datetime.now() + timedelta(days=14), "%Y-%m-%d")

    with table.batch_writer() as batch:
        for i in range(num_titles):
            table.put_item(
                Item={
                    'title_id':
                        str(uuid.uuid4())[:7]
                    ,
                    'title_name':
                        str(uuid.uuid4())[:15]
                    ,
                    'from':
                        _from
                    ,
                    'to': _to
                },
                ReturnValues='NONE',
                ReturnConsumedCapacity='NONE',
                # ExpressionAttributeNames={'#f': 'from', '#t': 'to'},
            )
