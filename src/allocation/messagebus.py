from __future__ import annotations
from typing import List, Dict, Callable, Type
from allocation import email, events, handlers, redis_pubsub


def handle(events_: List[events.Event], uow: unit_of_work.AbstractUnitOfWork):
    results = []
    while events_:
        event = events_.pop(0)
        print('handling message', event, flush=True)
        for handler in HANDLERS[type(event)]:
            r = handler(event, uow=uow)
            print('got result', r, flush=True)
            results.append(r)
    return results


HANDLERS = {
    events.BatchCreated: [handlers.add_batch],
    events.BatchQuantityChanged: [handlers.change_batch_quantity],
    events.AllocationRequest: [handlers.allocate],
    events.Deallocated: [handlers.allocate],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
    events.Allocated: [handlers.publish_allocated_event],

}  # type: Dict[Type[events.Event], List[Callable]]
