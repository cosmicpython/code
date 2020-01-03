from __future__ import annotations
from typing import List, Dict, Callable, Type, TYPE_CHECKING
from allocation.domain import events
from . import handlers
if TYPE_CHECKING:
    from allocation.service_layer import unit_of_work


def handle(event: events.Event, uow: unit_of_work.AbstractUnitOfWork):
    for handler in HANDLERS[type(event)]:
        handler(event, uow=uow)


HANDLERS = {
    events.BatchCreated: [handlers.add_batch],
    events.AllocationRequired: [handlers.allocate],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}  # type: Dict[Type[events.Event], List[Callable]]
