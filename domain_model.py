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


def allocate_to(line, allocation, quantities):
    for quantity in quantities:
        if quantity.sku == line.sku and quantity.quantity > line.quantity:
            line.allocation = allocation
            return

def allocate_to_stock(line, stock):
    allocate_to(line, 'STOCK', stock)

def allocate_to_shipment(line, shipment):
    allocate_to(line, shipment.id, shipment.lines)


def allocate_to_shipments(line, shipments):
    for shipment in shipments:
        allocate_to_shipment(line, shipment)
        if line.allocation is not None:
            return


def allocate(order, stock, shipments):
    if skus(order) <= skus(stock):
        for line in order:
            allocate_to_stock(line, stock)
        return
    shipments.sort(key=lambda s: s.eta)
    for shipment in shipments:
        if skus(order) <= skus(shipment):
            for line in order:
                allocate_to(line, shipment.id, shipment.lines)
            return

    for line in order:
        allocate_to_stock(line, stock)
        if line.allocation is None:
            allocate_to_shipments(line, shipments)
