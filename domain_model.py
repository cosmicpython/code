from dataclasses import dataclass

@dataclass
class Order(dict):
    def __init__(self, d):
        self.allocations = {}
        super().__init__(d)


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


def allocate_to(order, source, name):
    for sku, quantity in order.items():
        if source.get(sku, 0) > quantity:
            source[sku] -= quantity
            order.allocations[sku] = name


def allocate_to_stock(order, stock):
    allocate_to(order, stock, 'STOCK')

def allocate_to_shipment(order, shipment):
    allocate_to(order, shipment, shipment.id)




def allocate_to_shipments(order, shipments):
    for sku, quantity in order.items():
        if sku in order.allocations:
            continue
        for shipment in shipments:
            if shipment.get(sku, 0) > quantity:
                shipment[sku] -= quantity
                order.allocations[sku] = shipment.id
                break


def allocate(order, stock, shipments):
    if skus(order) <= skus(stock):
        allocate_to_stock(order, stock)
        return

    shipments.sort(key=lambda s: s.eta)

    for shipment in shipments:
        if skus(order) <= skus(shipment):
            allocate_to_shipment(order, shipment)
            return

    allocate_to_stock(order, stock)
    allocate_to_shipments(order, shipments)
