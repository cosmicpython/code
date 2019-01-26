class Order(dict):
    def __init__(self, lines):
        self.allocations = {}
        super().__init__(lines)


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


def allocate_line(sku, quantity, source, allocations):
    if source.get(sku, 0) > quantity:
        source[sku] -= quantity
        allocations[sku] = getattr(source, 'id', 'STOCK')

def allocate_to(order, source):
    allocations = {}
    for sku, quantity in order.items():
        allocate_line(sku, quantity, source, allocations)
    return allocations


def allocate_to_shipments(order, shipments, allocations):
    for sku, quantity in order.items():
        if sku in allocations:
            continue
        for shipment in shipments:
            allocate_line(sku, quantity, shipment, order.allocations)
            if sku in order.allocations:
                break



def allocate(order, stock, shipments):
    if skus(order) <= skus(stock):
        return allocate_to(order, stock)

    shipments.sort(key=lambda s: s.eta)

    for shipment in shipments:
        if skus(order) <= skus(shipment):
            return allocate_to(order, shipment)

    order.allocations = allocate_to(order, stock)
    allocate_to_shipments(order, shipments, order.allocations)
    return order.allocations
