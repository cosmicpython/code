from typing import List, Dict, Callable, Type
from allocation import email, events


def handle(events_: List[events.Event]):
    while events_:
        event = events_.pop(0)
        for handler in HANDLERS[type(event)]:
            handler(event)


def send_out_of_stock_notification(event: events.OutOfStock):
    email.send_mail(
        'stock@made.com',
        f'Out of stock for {event.sku}',
    )


HANDLERS = {
    events.OutOfStock: [send_out_of_stock_notification],

}  # type: Dict[Type[events.Event], List[Callable]]

