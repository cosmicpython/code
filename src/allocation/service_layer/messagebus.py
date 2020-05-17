# pylint: disable=broad-except, attribute-defined-outside-init
from __future__ import annotations
import logging
import time
import random
from typing import Callable, Dict, List, Union, Type, TYPE_CHECKING
from allocation.domain import commands, events

if TYPE_CHECKING:
    from . import unit_of_work

logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]


class MessageBus:

    def __init__(self):
        #event_handlers: Dict[Type[events.Event], List[Callable]],
        #command_handlers: Dict[Type[commands.Command], Callable]

        self.event_handlers = {}
        self.command_handlers = {}

    def register_handler(self, handler, message_type):
        if issubclass(message_type, events.Event):
            # Some awkward fumbling about here thaat could be avoided with defaultdicts
            handlers = self.event_handlers.get(message_type, [])
            handlers.append(handler)
            self.event_handlers[message_type] = handlers
        elif issubclass(message_type, commands.Command):
            assert message_type not in self.command_handlers # because command are intended to have a single recipient
            self.command_handlers[message_type] = handler
        else:
            raise Exception("Registration must be an with an event or command type: %s" % message_type)


    def handle(self, message: Message):
        queue = [message]
        while queue:
            message = queue.pop(0)
            if isinstance(message, events.Event):
                pending = self.handle_event(message)
                queue.extend(pending)
            elif isinstance(message, commands.Command):
                pending = self.handle_command(message)
                queue.extend(pending)
            else:
                raise Exception(f'{message} was not an Event or Command')


    def handle_event(self, event: events.Event):
        pending = []
        for handler in self.event_handlers[type(event)]:
            try:
                new_events = handler(event)
                if new_events:
                    pending.extend(new_events)
            except Exception:
                logger.exception('Exception handling event %s', event)
                continue
        return pending

    def handle_command(self, command: commands.Command):
        logger.debug('handling command %s', command)
        try:
            handler = self.command_handlers[type(command)]
            new_events = handler(command)
            if new_events:
                return new_events
            else:
                return []
        except Exception:
            logger.exception('Exception handling command %s', command)
            raise
