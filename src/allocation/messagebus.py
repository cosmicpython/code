from __future__ import annotations
from typing import List, Dict, Callable, Type
from allocation import email, events, services, redis_pubsub


def handle(events_: List[events.Event], uow: unit_of_work.AbstractUnitOfWork):
    while events_:
        event = events_.pop(0)
        for handler in HANDLERS[type(event)]:
            handler(event, uow=uow)


def send_out_of_stock_notification(
        event: events.OutOfStock, uow: unit_of_work.AbstractUnitOfWork
):
    email.send_mail(
        'stock@made.com',
        f'Out of stock for {event.sku}',
    )


def reallocate(
        event: events.Deallocated, uow: unit_of_work.AbstractUnitOfWork
):
    services.allocate(event.orderid, event.sku, event.qty, uow=uow)


def publish_allocated_event(
        event: events.Allocated, uow: unit_of_work.AbstractUnitOfWork,
):
    redis_pubsub.publish('line_allocated', event)


HANDLERS = {
    events.OutOfStock: [send_out_of_stock_notification],
    events.Allocated: [publish_allocated_event],
    events.Deallocated: [reallocate],

}  # type: Dict[Type[events.Event], List[Callable]]
