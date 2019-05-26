from __future__ import annotations
from typing import List, Dict, Callable, Type
from allocation import email, events, handlers, redis_pubsub


def handle(events_: List[events.Event], uow: unit_of_work.AbstractUnitOfWork):
    while events_:
        event = events_.pop(0)
        for handler in HANDLERS[type(event)]:
            handler(event, uow=uow)


HANDLERS = {
    events.BatchCreated: [handlers.add_batch],
    events.BatchQuantityChanged: [handlers.change_batch_quantity],
    events.AllocationRequest: [handlers.allocate],
    events.Deallocated: [handlers.allocate],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
    events.Allocated: [handlers.publish_allocated_event],

}  # type: Dict[Type[events.Event], List[Callable]]
