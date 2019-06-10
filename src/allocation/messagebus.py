from __future__ import annotations
import traceback
from typing import List, Dict, Callable, Type, Union, TYPE_CHECKING
from allocation import commands, events, handlers

if TYPE_CHECKING:
    from allocation import unit_of_work

Message = Union[commands.Command, events.Event]


def handle(message_queue: List[Message], uow: unit_of_work.AbstractUnitOfWork):
    while message_queue:
        m = message_queue.pop(0)
        if isinstance(m, events.Event):
            handle_event(m, uow)
        elif isinstance(m, commands.Command):
            handle_command(m, uow)
        else:
            raise Exception(f'{m} was not an Event or Command')


def handle_event(event: events.Event, uow: unit_of_work.AbstractUnitOfWork):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            print('handling event', event, 'with handler', handler, flush=True)
            handler(event, uow=uow)
        except:
            print(f'Exception handling event {event}\n:{traceback.format_exc()}')
            continue


def handle_command(command, uow: unit_of_work.AbstractUnitOfWork):
    print('handling command', command, flush=True)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        return handler(command, uow=uow)
    except Exception as e:
        print(f'Exception handling command {command}: {e}')
        raise e


EVENT_HANDLERS = {
    events.Allocated: [handlers.publish_allocated_event],
    events.Deallocated: [handlers.allocate],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.Allocate: handlers.allocate,
    commands.CreateBatch: handlers.add_batch,
    commands.ChangeBatchQuantity: handlers.change_batch_quantity,
}  # type: Dict[Type[commands.Command], Callable]


