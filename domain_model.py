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


def allocate_to_sources(order, sources):
    allocations = {}
    for sku, quantity in order.items():
        if sku in allocations:
            continue
        for source in sources:
            allocate_line(sku, quantity, source, allocations)
            if sku in allocations:
                break
    return allocations



def allocate(order, stock, shipments):
    if skus(order) <= skus(stock):
        return allocate_to(order, stock)

    shipments.sort(key=lambda s: s.eta)

    for shipment in shipments:
        if skus(order) <= skus(shipment):
            return allocate_to(order, shipment)

    return allocate_to_sources(order, [stock] + shipments)
