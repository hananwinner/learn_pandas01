import time
import boto3
import json
import threading
import queue


class AggregatorAsyncSqsHandler(object):
    def __init__(self):
        self._event_pub = AsyncSqsPublisher('new_event')
        self._reser_pub = AsyncSqsPublisher('new_reservation')
        self._event_pub.start()
        self._reser_pub.start()

    def stop(self):
        self._event_pub.stop()
        self._reser_pub.stop()
        self._event_pub.join(timeout=1)
        self._reser_pub.join(timeout=1)

    def event_user_booked(self, user_id, day, title_id):
        message = {
            'user_id': user_id,
            'day': day,
            'title_id': title_id
        }
        self._reser_pub.add_message(message)

    def event_booking_canceled(self, user_id, day, title_id):
        pass

    def event_event_booked(self,day, title_id, num_tickets, bids_total):
        message = {
            'title_id': title_id,
            'day': day,
            'num_tickets': num_tickets,
            'bids_total': float(bids_total),
        }
        self._event_pub.add_message(message)


class AsyncSqsPublisher(threading.Thread):
    def __init__(self, sqs_queue_name):
        threading.Thread.__init__(self)
        self._queue = queue.Queue()
        sqs = boto3.resource('sqs')
        self._sqs_queue = sqs.get_queue_by_name(QueueName=sqs_queue_name)
        self._stop_running = False

    def run(self) -> None:
        cur_sleep = 0.1
        while not self._stop_running:
            time.sleep(cur_sleep)
            try:
                message = self._queue.get(block=False)
            except queue.Empty:
                message = None
            if message is not None:
                if self._send(message):
                    cur_sleep = 0.1
                    self._queue.task_done()
                else:
                    cur_sleep = 0.2
            else:
                cur_sleep = 0.2

        try:
            while True:
                message = self._queue.get(block=False)
                self._send(message)
                self._queue.task_done()
        except queue.Empty:
            pass


    def stop(self):
        self._stop_running = True

    def add_message(self, message):
        self._queue.put(message)

    def _send(self, message):
        response = self._sqs_queue.send_message(
            MessageBody=json.dumps(message),
        )
        status_code = response['ResponseMetadata']['HTTPStatusCode']
        if status_code != 200:
            print('message status code {}\n{}'.format(status_code, message))
            return False
        else:
            return True
