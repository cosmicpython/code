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
    sku: str
    quantity: int
    shipment_id: str


def to_list(fn):
    return lambda *a, **kw: list(fn(*a, **kw))


def allocate_to_stock(order_id, line, stock):
    for stock_line in stock:
        if stock_line.sku == line.sku:
            return Allocation(order_id, line.sku, line.quantity, shipment_id=None)

def allocate_to_shipments(order_id, line, shipments):
    for shipment in shipments:
        for shipment_line in shipment.lines:
            if shipment_line.sku == line.sku:
                return Allocation(order_id, line.sku, line.quantity, shipment.id)

@to_list
def allocate(order, stock, shipments):
    for line in order.lines:
        a = allocate_to_stock(order.id, line, stock)
        if a:
            yield a
        else:
            yield allocate_to_shipments(order.id, line, shipments)


