# pylint: disable=broad-except, attribute-defined-outside-init
from __future__ import annotations
import logging
import time
import random
from typing import Callable, Dict, List, Union, Type, TYPE_CHECKING
from allocation.domain import commands, events
from allocation.service_layer.unit_of_work import SqlAlchemyUnitOfWork

if TYPE_CHECKING:
    from . import unit_of_work

logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]


class MessageBus:

    def __init__(
        self,
        event_handlers: Dict[Type[events.Event], List[Callable]],
        command_handlers: Dict[Type[commands.Command], Callable]
    ):
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers

    def handle(self, message: Message, uow):
        queue = [message]
        while queue:
            message = queue.pop(0)
            if isinstance(message, events.Event):
                pending = self.handle_event(message, uow)
                queue.extend(pending)
            elif isinstance(message, commands.Command):
                pending = self.handle_command(message, uow)
                queue.extend(pending)
            else:
                raise Exception(f'{message} was not an Event or Command')


    def handle_event(self, event: events.Event, uow):
        pending = []
        for handler in self.event_handlers[type(event)]:
            try:
                logger.debug('handling event %s with handler %s', event, handler)
                if 'uow' in handler.func.__code__.co_varnames:
                    handler(event, uow=uow)
                else:
                    handler(event)
                new_events = uow.collect_new_events()
                pending.extend(new_events)
            except Exception:
                logger.exception('Exception handling event %s', event)
                continue
        return pending

    def handle_command(self, command: commands.Command, uow):
        logger.debug('handling command %s', command)
        try:
            handler = self.command_handlers[type(command)]
            if 'uow' in handler.func.__code__.co_varnames:
                handler(command, uow=uow)
            else:
                handler(command)
            #ts = random.choice([0.1, 0.1, 1])
            #time.sleep(ts)
            return uow.collect_new_events()
        except Exception:
            logger.exception('Exception handling command %s', command)
            raise
