# pylint: disable=bare-except
from __future__ import annotations
import logging
import inspect
from typing import List, Dict, Callable, Type, Union, TYPE_CHECKING
from allocation.domain import commands, events
from . import handlers

if TYPE_CHECKING:
    from allocation.service_layer import unit_of_work

logger = logging.getLogger(__name__)

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
                logger.debug('handling event %s with handler %s', event, handler)
                self.call_handler_with_dependencies(handler, event)
            except:
                logger.exception('Exception handling event %s', event)
                continue

    def handle_command(self, command: commands.Command):
        logger.debug('handling command %s', command)
        try:
            handler = COMMAND_HANDLERS[type(command)]
            self.call_handler_with_dependencies(handler, command)
        except Exception:
            logger.exception('Exception handling command %s', command)
            raise


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
