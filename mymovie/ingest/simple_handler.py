import boto3
import json


class SimpleSqsToDynDbHandler(object):
    def __init__(self, queue_name, target_table_name):
        sqs = boto3.resource('sqs')
        self._queue = sqs.get_queue_by_name(QueueName=queue_name)
        dynamodb = boto3.resource('dynamodb')
        self._target_table = dynamodb.Table(target_table_name)

    def poll(self):
        messages = self._queue.receive_messages(
            MaxNumberOfMessages=10,
        )
        return messages

    @staticmethod
    def get_data_dict(message):
        return json.loads(message["Body"])

    @staticmethod
    def delete_message(message):
        message.delete()

    def try_make_item(self, data):
        pass

    def main(self):
        while True:
            messages = self.poll()
            for a_message in messages:
                data = self.get_data_dict(a_message)
                try:
                    item = self.try_make_item(data)
                    self._target_table.put_item(item)
                    self.delete_message(a_message)
                except OSError:
                    pass
                except ValueError:
                    self.delete_message(a_message)