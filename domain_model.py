from dataclasses import dataclass

class Allocation(dict):

    @property
    def skus(self):
        return self.keys()

    def supplement_with(self, allocation):
        for sku, quantity in allocation.items():
            if sku in self:
                continue
            self[sku] = quantity


@dataclass
class Order:
    lines: dict
    allocation: Allocation = None

    @property
    def skus(self):
        return self.lines.keys()

    @property
    def fully_allocated(self):
        return self.allocation.skus == self.skus


    def allocate(self, stock, shipments):
        self.allocation = Allocation()
        for source in [stock] + sorted(shipments, key=lambda x: x.eta):
            source_allocation = Allocation({
                sku: source
                for sku, quantity in self.lines.items()
                if source.can_allocate(sku, quantity)
            })
            if source_allocation.skus == self.skus:
                self.allocation = source_allocation
                return
            self.allocation.supplement_with(source_allocation)


class Stock(dict):

    def can_allocate(self, sku, quantity):
        return sku in self and self[sku] > quantity


@dataclass
class Shipment(Stock):

    def __init__(self, lines, eta):
        self.eta = eta
        super().__init__(lines)

    def can_allocate(self, sku, quantity):
        return sku in self and self[sku] > quantity

