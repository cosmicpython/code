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


def allocate_line(order, sku, quantity, source):
    if source.get(sku, 0) > quantity:
        source[sku] -= quantity
        order.allocations[sku] = getattr(source, 'id', 'STOCK')

def allocate_to(order, source):
    for sku, quantity in order.items():
        allocate_line(order, sku, quantity, source)


def allocate_to_shipments(order, shipments):
    for sku, quantity in order.items():
        if sku in order.allocations:
            continue
        for shipment in shipments:
            allocate_line(order, sku, quantity, shipment)
            if sku in order.allocations:
                break



def allocate(order, stock, shipments):
    if skus(order) <= skus(stock):
        allocate_to(order, stock)
        return order.allocations

    shipments.sort(key=lambda s: s.eta)

    for shipment in shipments:
        if skus(order) <= skus(shipment):
            allocate_to(order, shipment)
            return order.allocations

    allocate_to(order, stock)
    allocate_to_shipments(order, shipments)
    return order.allocations
