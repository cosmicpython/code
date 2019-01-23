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


@to_list
def allocate(order, stock, shipments):
    for line in order.lines:
        for stock_line in stock:
            yield Allocation(order.id, line.sku, line.quantity, shipment_id=None)
        for shipment in shipments:
            for shipment_line in shipment.lines:
                if shipment_line.sku == line.sku:
                    yield Allocation(order.id, line.sku, line.quantity, shipment.id)

