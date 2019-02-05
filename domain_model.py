from dataclasses import dataclass
from datetime import date

class Allocation(dict):

    @property
    def skus(self):
        return self.keys()


@dataclass
class Order:
    lines: dict
    allocations: dict = None

    @property
    def skus(self):
        return self.lines.keys()

    @property
    def fully_allocated(self):
        return self.allocations.skus == self.skus


    def allocate(self, stock, shipments):
        self.allocations = {}
        for source in [stock] + shipments:
            allocation = Allocation({
                sku: source
                for sku, quantity in self.lines.items()
                if source.can_allocate(sku, quantity)
            })
            if allocation.skus == self.skus:
                self.allocations = allocation
                return
            allocation.update(self.allocations)
            self.allocations = allocation


@dataclass
class Stock:
    lines: dict
    eta: date = None

    def can_allocate(self, sku, quantity):
        return sku in self.lines and self.lines[sku] > quantity

