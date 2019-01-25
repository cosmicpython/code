from dataclasses import dataclass
from datetime import date

@dataclass
class Line:
    sku: str
    quantity: int


@dataclass
class OrderLine(Line):
    allocation: str = None


@dataclass
class Shipment:
    id: str
    eta: date
    lines: list


def allocate_to_stock(line, stock):
    for stock_line in stock:
        if stock_line.sku == line.sku:
            line.allocation = 'STOCK'

def allocate_to_shipments(line, shipments):
    for shipment in shipments:
        for shipment_line in shipment.lines:
            if shipment_line.sku == line.sku:
                line.allocation = shipment.id

def allocate(order, stock, shipments):
    for line in order:
        allocate_to_stock(line, stock)
        if not line.allocation:
            allocate_to_shipments(line, shipments)

