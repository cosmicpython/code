# pylint: disable=too-few-public-methods
import asyncio
from contextvars import ContextVar
from dataclasses import dataclass


class Event:
    pass


@dataclass
class Allocated(Event):
    orderid: str
    sku: str
    qty: int
    batchref: str


@dataclass
class Deallocated(Event):
    orderid: str
    sku: str
    qty: int


@dataclass
class OutOfStock(Event):
    sku: str


event_queue: ContextVar[asyncio.Queue[Event]] = ContextVar('event_queue')


def issue_event(event: Event) -> None:
    queue = event_queue.get(asyncio.Queue[Event]())
    queue.put_nowait(event)
    event_queue.set(queue)
