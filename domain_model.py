class Allocation(dict):

    def __init__(self, d, order):
        self.order = order
        super().__init__(d)

    @staticmethod
    def for_source(order, source):
        return Allocation({
            sku: source
            for sku, quantity in order.items()
            if source.can_allocate(sku, quantity)
        }, order=order)


    @staticmethod
    def for_order(order, stock, shipments):
        allocation = Allocation({}, order=order)
        for source in [stock] + sorted(shipments):
            source_allocation = Allocation.for_source(order, source)
            allocation.supplement_with(source_allocation)
        return allocation


    def supplement_with(self, allocation):
        for sku, quantity in allocation.items():
            if sku in self:
                continue
            self[sku] = quantity


    def decrement_source_quantities(self):
        for sku, source in self.items():
            source[sku] -= self.order[sku]


class Order(dict):

    def allocate(self, stock, shipments):
        self.allocation = Allocation.for_order(self, stock, shipments)
        self.allocation.decrement_source_quantities()


class Stock(dict):

    def can_allocate(self, sku, quantity):
        return sku in self and self[sku] > quantity

    def allocate(self, sku, quantity):
        self[sku] -= quantity


class Shipment(Stock):

    def __lt__(self, other):
        return self.eta < other.eta

    def __init__(self, lines, eta):
        self.eta = eta
        super().__init__(lines)

