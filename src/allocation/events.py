from datetime import date
from typing import Optional
from dataclasses import dataclass

class Event:
    pass

@dataclass
class AllocationRequest(Event):
    orderid: str
    sku: str
    qty: int

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

@dataclass
class BatchCreated(Event):
    ref: str
    sku: str
    qty: int
    eta: Optional[date] = None

@dataclass
class BatchQuantityChanged(Event):
    ref: str
    qty: int
