import boto3
import json


class SimpleSqsToDynDbHandler(object):
    def __init__(self, queue_name, target_table_name,
                 via_event_source_mapping=True):
        self._wrapped_mode = via_event_source_mapping
        if not self._wrapped_mode:
            sqs = boto3.resource('sqs')
            self._queue = sqs.get_queue_by_name(QueueName=queue_name)
        dynamodb = boto3.resource('dynamodb')
        self._target_table = dynamodb.Table(target_table_name)

    def _poll(self):
        messages = self._queue.receive_messages(
            MaxNumberOfMessages=10,
        )
        return messages

    def _get_data_dict(self, message):
        if self._wrapped_mode:
            return json.loads(message["body"])
        else:
            return json.loads(message.body)

    @staticmethod
    def _delete_message(message):
        message.delete()

    def _try_make_item(self, data):
        pass

    def process_messages(self, messages):
        for a_message in messages:
            print(a_message)
            data = self._get_data_dict(a_message)
            try:
                item = self._try_make_item(data)
                if item is not None:
                    self._target_table.put_item(Item=item)
                if not self._wrapped_mode:
                    self._delete_message(a_message)
            except OSError:
                pass
            except ValueError:
                if not self._wrapped_mode:
                    self._delete_message(a_message)

    def main(self):
        if self._wrapped_mode:
            raise NotImplementedError('dont run main in wrapped-mode, use process_messages')
        while True:
            messages = self._poll()
            self.process_messages(messages)
