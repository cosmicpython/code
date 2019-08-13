# pylint: disable=too-few-public-methods
from dataclasses import dataclass


class Event:
    pass


@dataclass
class OutOfStock(Event):
    sku: str
