from dataclasses import dataclass

@dataclass
class Line:
    sku: str
    quantity: int




@dataclass
class OrderLine(Line):
    allocation: str = None


@dataclass
class Shipment(dict):
    def __init__(self, id, eta, lines):
        self.id = id
        self.eta = eta
        super().__init__(lines)


def skus(thing):
    try:
        return {line.sku for line in thing}
    except:
        return thing.keys()


def allocate_to(line, allocation, source):
    try:
        if source.get(line.sku, 0) > line.quantity:
            line.allocation = allocation
            source[line.sku] -= line.quantity

    except AttributeError:
        for source_line in source:
            if source_line.sku == line.sku and source_line.quantity > line.quantity:
                line.allocation = allocation
                source_line.quantity -= line.quantity
                return

def allocate_to_stock(order, stock):
    for line in order:
        allocate_to(line, 'STOCK', stock)


def allocate_to_shipment(order, shipment):
    for line in order:
        allocate_to(line, shipment.id, shipment)


def allocate_to_shipments(order, shipments):
    for line in order:
        _allocate_line_to_shipments(line, shipments)


def _allocate_line_to_shipments(line, shipments):
    for shipment in shipments:
        allocate_to(line, shipment.id, shipment)
        if line.allocation:
            return


def allocate(order, stock, shipments):
    if skus(order) <= skus(stock):
        allocate_to_stock(order, stock)
        return

    shipments.sort(key=lambda s: s.eta)

    for shipment in shipments:
        if skus(order) <= skus(shipment):
            allocate_to_shipment(order, shipment)
            return

    allocate_to_shipments(order, shipments)
    allocate_to_stock(order, stock)
