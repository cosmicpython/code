from dataclasses import dataclass
from datetime import date

class Allocation(dict):

    @property
    def skus(self):
        return self.keys()


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
        self.allocation = {}
        for source in [stock] + sorted(shipments, key=lambda x: x.eta):
            allocation = Allocation({
                sku: source
                for sku, quantity in self.lines.items()
                if source.can_allocate(sku, quantity)
            })
            if allocation.skus == self.skus:
                self.allocation = allocation
                return
            allocation.update(self.allocation)
            self.allocation = allocation


@dataclass
class Stock:
    lines: dict
    eta: date = None

    def can_allocate(self, sku, quantity):
        return sku in self.lines and self.lines[sku] > quantity

