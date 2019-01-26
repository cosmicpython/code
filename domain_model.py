class Shipment(dict):
    def __init__(self, eta, lines):
        self.eta = eta
        super().__init__(lines)


def skus(d):
    return set(d.keys())


def allocate_to(order, source):
    return {
        sku: source
        for sku, quantity in order.items()
        if sku in source
        and source[sku] > quantity
    }


def allocate(order, stock, shipments):
    stock_allocation = allocate_to(order, stock)
    if skus(stock_allocation) == skus(order):
        return stock_allocation

    shipments.sort(key=lambda s: s.eta)

    shipment_allocations = []
    for shipment in shipments:
        shipment_allocation = allocate_to(order, shipment)
        if skus(shipment_allocation) == skus(order):
            return shipment_allocation
        shipment_allocations.append(shipment_allocation)

    mixed_allocation = {}
    for allocation in shipment_allocations + [stock_allocation]:
        mixed_allocation.update(allocation)
    return mixed_allocation

