# pylint: disable=broad-except, attribute-defined-outside-init
from __future__ import annotations

import asyncio
import logging
from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Any, Callable, Dict, List, Optional, Protocol, TYPE_CHECKING, Type, Union

from allocation.domain import commands, events

if TYPE_CHECKING:
    class EventResolver(Protocol):
        async def __call__(self, event: events.Event, /) -> None:
            ...


logger = logging.getLogger(__name__)


class CollectAndHandleLocalEvents(AbstractAsyncContextManager['CollectAndHandleLocalEvents']):
    _handle_event: EventResolver

    def __init__(self, handle_event: EventResolver) -> None:
        self._handle_event = handle_event

    async def __aenter__(self) -> CollectAndHandleLocalEvents:
        events.event_queue.set(asyncio.Queue())
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        queue = events.event_queue.get()
        while not queue.empty():
            event = await queue.get()
            asyncio.create_task(self._handle_event(event))
            queue.task_done()


Message = Union[commands.Command, events.Event]


class MessageBus:
    def __init__(
        self,
        event_handlers: Dict[Type[events.Event], List[Callable]],
        command_handlers: Dict[Type[commands.Command], Callable],
    ):
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers

    async def handle_event(self, event: events.Event, /) -> None:
        # explicitly create task for local contextvars  (events.event_queue)
        await asyncio.create_task(self.handle_event(event))

    async def _handle_event(self, event: events.Event, /) -> None:
        async with CollectAndHandleLocalEvents(self._handle_event):
            # TODO: parallelize with asyncio.gather
            for handler in self.event_handlers.get(type(event), []):
                try:
                    logger.debug('handling event %s with handler %s', event, handler)  # noqa: FKA01
                    await handler(event)
                except Exception:
                    logger.exception('Exception handling event %s', event)
                    continue

    async def handle_command(self, command: commands.Command, /) -> Any:
        # explicitly create task for local contextvars  (events.event_queue)
        return await asyncio.create_task(self._handle_command(command))

    async def _handle_command(self, command: commands.Command, /) -> Any:
        async with CollectAndHandleLocalEvents(self._handle_event):
            logger.debug('handling command %s', command)
            try:
                handler = self.command_handlers[type(command)]
                return await handler(command)
            except Exception:
                logger.exception('Exception handling command %s', command)
                raise
