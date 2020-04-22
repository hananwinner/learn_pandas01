# import time
# import boto3
# import queue
#
# class BatchSqsHandler(object):
#     def __init__(self, batch_reservation_size=100):
#         self._batch_reservation_size = batch_reservation_size
#         self._events = queue.Queue()
#         self._cur_batch_reservations = None
#
#     def event_event_booked(self, day, title_id, num_tickets, bids_total):
#         self._cur_
#         self._events.put({
#             'title_id': title_id,
#             'day': day,
#             'num_tickets': num_tickets,
#             'bids_total': bids_total,
#         })
#
#     def event_user_booked(self, user_id, day, title_id):
#         self._cur_batch_reservations.append({
#             'user_id': user_id,
#             'day': day,
#             'title_id': title_id
#         })
#         if len(self._cur_batch_reservations) >= self._batch_reservation_size:
#             if self._send_message():
#                 self._cur_batch_reservations = []
#
#     def _send_message(self):
#
#
#     def flush(self):
#         if self._cur_event is not None:
#             sent = self._send_message()
#             while not sent:
#                 time.sleep(1)
#                 self._send_message()
#
