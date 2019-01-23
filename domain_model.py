from dataclasses import dataclass
from datetime import date

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
    eta: date
    lines: list


@dataclass
class Allocation:
    order_id: str
    shipment_id: str
    sku: str
    quantity: int



def allocate(order, stock, shipments):
    line = order.lines[0]
    if stock:
        return [
            Allocation(order.id, None, line.sku, line.quantity)
        ]

    return [
        Allocation(order.id, shipments[0].id, line.sku, line.quantity)
    ]
