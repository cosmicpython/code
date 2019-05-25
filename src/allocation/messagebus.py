from __future__ import annotations
from typing import List, Dict, Callable, Type, TYPE_CHECKING
from allocation import events, handlers
if TYPE_CHECKING:
    from allocation import unit_of_work


def handle(event: events.Event, uow: unit_of_work.AbstractUnitOfWork):
    results = []
    for handler in HANDLERS[type(event)]:
        r = handler(event, uow=uow)
        results.append(r)
    return results



HANDLERS = {
    events.BatchCreated: [handlers.add_batch],
    events.BatchQuantityChanged: [handlers.change_batch_quantity],
    events.AllocationRequired: [handlers.allocate],
    events.OutOfStock: [handlers.send_out_of_stock_notification],

}  # type: Dict[Type[events.Event], List[Callable]]
