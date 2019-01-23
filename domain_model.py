from dataclasses import dataclass
from datetime import datetime

@dataclass
class Order:
    id: str
    lines: list


@dataclass
class OrderLine:
    sku: str
    quantity: int


@dataclass
class Stock:
    sku: str
    quantity: int


@dataclass
class Shipment:
    id: str
    sku: str
    quantity: int
    eta: datetime


@dataclass
class Allocation:
    order_id: str
    shipment_id: str
    sku: str
    quantity: int



def allocate(order, stock, shipments):
    line = order.lines[0]
    return [
        Allocation(order.id, None, line.sku, line.quantity)
    ]
