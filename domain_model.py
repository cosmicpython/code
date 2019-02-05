from dataclasses import dataclass
from datetime import date

@dataclass
class Order:
    lines: dict
    allocations: dict = None

    @property
    def fully_allocated(self):
        return set(self.allocations.keys()) == set(self.lines.keys())


    def allocate(self, stock, shipments):
        self.allocations = {}
        for source in [stock] + shipments:
            allocation = {
                sku: source
                for sku, quantity in self.lines.items()
                if source.can_allocate(sku, quantity)
            }
            if set(allocation.keys()) == set(self.lines):
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


