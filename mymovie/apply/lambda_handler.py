from mymovie.apply.new_event import NewEventConsumer
from mymovie.apply.new_reservation import NewReservationConsumer


def handle_events(event, context):
    NewEventConsumer().process_messages(event["Records"])


def handle_reservations(event, context):
    NewReservationConsumer().process_messages(event["Records"])
