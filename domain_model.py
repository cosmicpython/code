class Order(dict):

    def allocate(self, stock, shipments):
        self.allocation = self.find_allocation(stock, shipments)
        self.decrement_source_quantities()

    def find_allocation(self, stock, shipments):
        ordered_sources = [stock] + sorted(shipments)
        allocation = {}
        for source in reversed(ordered_sources):
            allocation.update(source.allocation_for(self))
        return allocation

    def decrement_source_quantities(self):
        for sku, source in self.allocation.items():
            source[sku] -= self[sku]



class Stock(dict):

    def allocation_for(self, order):
        return {
            sku: self
            for sku, quantity in order.items()
            if sku in self
            and self[sku] > quantity
        }


class Shipment(Stock):

    def __init__(self, d, eta):
        self.eta = eta
        super().__init__(d)

    def __lt__(self, other):
        return self.eta < other.eta


