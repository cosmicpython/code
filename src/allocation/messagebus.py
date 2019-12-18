# pylint: disable=bare-except
from __future__ import annotations
import logging
import inspect
import traceback
from typing import List, Dict, Callable, Type, Union, TYPE_CHECKING
from allocation import commands, events, handlers

if TYPE_CHECKING:
    from allocation import notifications, unit_of_work

Message = Union[commands.Command, events.Event]


class MessageBus:

    def __init__(
            self,
            uow: unit_of_work.AbstractUnitOfWork,
            notifications: notifications.AbstractNotifications,
            publish: Callable,
    ):
        self.uow = uow
        self.dependencies = dict(uow=uow, notifications=notifications, publish=publish)

    def handle(self, message: Message):
        if isinstance(message, events.Event):
            self.handle_event(message)
        elif isinstance(message, commands.Command):
            self.handle_command(message)
        else:
            raise Exception(f'{message} was not an Event or Command')



    def handle_event(self, event: events.Event):
        for handler in EVENT_HANDLERS[type(event)]:
            try:
                logging.debug('handling event %s with handler %s', event, handler)
                self.call_handler_with_dependencies(handler, event)
            except:
                logging.exception('Exception handling event %s', event)
                continue

    def handle_command(self, command: commands.Command):
        logging.debug('handling command %s', command)
        try:
            handler = COMMAND_HANDLERS[type(command)]
            self.call_handler_with_dependencies(handler, command)
        except Exception:
            logging.exception('Exception handling command %s', command)
            raise

    def call_handler_with_dependencies(self, handler: Callable, message: Message):
        params = inspect.signature(handler).parameters
        deps = {
            name: dependency for name, dependency in self.dependencies.items()
            if name in params
        }
        handler(message, **deps)


EVENT_HANDLERS = {
    events.Allocated: [
        handlers.publish_allocated_event,
        handlers.add_allocation_to_read_model
    ],
    events.Deallocated: [
        handlers.remove_allocation_from_read_model,
        handlers.reallocate,
    ],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.Allocate: handlers.allocate,
    commands.CreateBatch: handlers.add_batch,
    commands.ChangeBatchQuantity: handlers.change_batch_quantity,
}  # type: Dict[Type[commands.Command], Callable]
