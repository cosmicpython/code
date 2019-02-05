class Allocation(dict):

    def __init__(self, d, order):
        self.order = order
        super().__init__(d)

    @property
    def skus(self):
        return self.keys()

    @staticmethod
    def for_(order, source):
        return Allocation({
            sku: source
            for sku, quantity in order.items()
            if source.can_allocate(sku, quantity)
        }, order=order)

    def supplement_with(self, allocation):
        for sku, quantity in allocation.items():
            if sku in self:
                continue
            self[sku] = quantity

    @property
    def is_complete(self):
        return self.skus == self.order.skus

    def apply(self):
        for sku, source in self.items():
            source[sku] -= self.order[sku]


class Order(dict):

    @property
    def skus(self):
        return self.keys()

    @property
    def fully_allocated(self):
        return self.allocation.is_complete

    def allocate(self, stock, shipments):
        self.allocation = Allocation({}, order=self)
        for source in [stock] + sorted(shipments):
            source_allocation = Allocation.for_(self, source)
            if source_allocation.is_complete:
                self.allocation = source_allocation
                self.allocation.apply()
                return
            self.allocation.supplement_with(source_allocation)
        self.allocation.apply()


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

