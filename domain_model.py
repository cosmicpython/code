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


def skus(thing):
    try:
        return {line.sku for line in thing}
    except TypeError:
        return {line.sku for line in thing.lines}



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
    if skus(order) <= skus(stock):
        for line in order:
            line.allocation = 'STOCK'
        return
    shipments.sort(key=lambda s: s.eta)
    for shipment in shipments:
        if skus(order) <= skus(shipment):
            for line in order:
                line.allocation = shipment.id
            return

    for line in order:
        allocate_to_stock(line, stock)
        if line.allocation is None:
            allocate_to_shipments(line, shipments)
