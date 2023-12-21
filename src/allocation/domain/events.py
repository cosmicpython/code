# pylint: disable=too-few-public-methods
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
