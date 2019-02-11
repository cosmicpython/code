def allocate(order, warehouse, shipments):
    ordered_sources = [warehouse] + sorted(shipments)
    allocation = {}
    for source in reversed(ordered_sources):
        allocation.update(source.allocation_for(order))
    decrement_source_quantities(order, allocation)
    return allocation

def decrement_source_quantities(order, allocation):
    for sku, source in allocation.items():
        source[sku] -= order[sku]


class Order(dict):
    pass


class _Stock(dict):

    def allocation_for(self, order):
        return {
            sku: self
            for sku, quantity in order.items()
            if sku in self
            and self[sku] > quantity
        }


class Warehouse(_Stock):
    pass



class Shipment(_Stock):

    def __init__(self, d, eta):
        self.eta = eta
        super().__init__(d)

    def __lt__(self, other):
        return self.eta < other.eta


