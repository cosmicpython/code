# pylint: disable=bare-except
from __future__ import annotations
import inspect
import traceback
from typing import List, Dict, Callable, Type, Union, TYPE_CHECKING
from allocation import commands, events, handlers

if TYPE_CHECKING:
    from allocation import unit_of_work

Message = Union[commands.Command, events.Event]


class MessageBus:

    def __init__(
            self,
            uow: unit_of_work.AbstractUnitOfWork,
            send_mail: Callable,
            publish: Callable,
    ):
        self.uow = uow
        self.dependencies = dict(uow=uow, send_mail=send_mail, publish=publish)

    def handle(self, message_queue: List[Message]):
        while message_queue:
            m = message_queue.pop(0)
            print('handling message', m, flush=True)
            if isinstance(m, events.Event):
                self.handle_event(m)
            elif isinstance(m, commands.Command):
                self.handle_command(m)
            else:
                raise Exception(f'{m} was not an Event or Command')
            message_queue.extend(self.uow.collect_events())


    def handle_event(self, event: events.Event):
        for handler in EVENT_HANDLERS[type(event)]:
            try:
                print('handling event', event, 'with handler', handler, flush=True)
                self.call_handler_with_dependencies(handler, event)
            except:
                print(f'Exception handling event {event}\n:{traceback.format_exc()}')
                continue

    def handle_command(self, command: commands.Command):
        print('handling command', command, flush=True)
        try:
            handler = COMMAND_HANDLERS[type(command)]
            return self.call_handler_with_dependencies(handler, command)
        except Exception as e:
            print(f'Exception handling command {command}: {e}')
            raise e

    def call_handler_with_dependencies(self, handler: Callable, message: Message):
        params = inspect.signature(handler).parameters
        deps = {
            name: dependency for name, dependency in self.dependencies.items()
            if name in params
        }
        return handler(message, **deps)


EVENT_HANDLERS = {
    events.Allocated: [
        handlers.publish_allocated_event, handlers.add_allocation_to_read_model
    ],
    events.Deallocated: [
        handlers.remove_allocation_from_read_model, handlers.allocate
    ],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.Allocate: handlers.allocate,
    commands.CreateBatch: handlers.add_batch,
    commands.ChangeBatchQuantity: handlers.change_batch_quantity,
}  # type: Dict[Type[commands.Command], Callable]

