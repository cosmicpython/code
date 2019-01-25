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
    allocation: str = None


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
    sku: str
    quantity: int
    shipment_id: str


def allocate_to_stock(order_id, line, stock):
    for stock_line in stock:
        if stock_line.sku == line.sku:
            line.allocation = 'warehouse'

def allocate_to_shipments(order_id, line, shipments):
    for shipment in shipments:
        for shipment_line in shipment.lines:
            if shipment_line.sku == line.sku:
                line.allocation = shipment.id

def allocate(order, stock, shipments):
    for line in order.lines:
        allocate_to_stock(order.id, line, stock)
        if not line.allocation:
            allocate_to_shipments(order.id, line, shipments)

