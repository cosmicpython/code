from dataclasses import dataclass

class Allocation(dict):

    @property
    def skus(self):
        return self.keys()

    @staticmethod
    def for_(order, source):
        return Allocation({
            sku: source
            for sku, quantity in order.lines.items()
            if source.can_allocate(sku, quantity)
        })


    def supplement_with(self, allocation):
        for sku, quantity in allocation.items():
            if sku in self:
                continue
            self[sku] = quantity

    def fully_allocates(self, order):
        return self.skus == order.skus




@dataclass
class Order:
    lines: dict
    allocation: Allocation = None

    @property
    def skus(self):
        return self.lines.keys()

    @property
    def fully_allocated(self):
        return self.allocation.fully_allocates(self)

    def allocate(self, stock, shipments):
        self.allocation = Allocation()
        for source in [stock] + sorted(shipments):
            source_allocation = Allocation.for_(self, source)
            if source_allocation.fully_allocates(self):
                self.allocation = source_allocation
                return
            self.allocation.supplement_with(source_allocation)


class Stock(dict):

    def can_allocate(self, sku, quantity):
        return sku in self and self[sku] > quantity


class Shipment(Stock):

    def __lt__(self, other):
        return self.eta < other.eta

    def __init__(self, lines, eta):
        self.eta = eta
        super().__init__(lines)

    def can_allocate(self, sku, quantity):
        return sku in self and self[sku] > quantity

