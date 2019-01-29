from dataclasses import dataclass
from datetime import date

@dataclass
class Order:
    lines: dict
    allocations: dict = None

    def allocate(self, stock, shipments):
        self.allocations = {
            key: stock
            for key in self.lines
        }
        for s in shipments:
            self.allocations.update({
                key: s
                for key in self.lines
            })


@dataclass
class Stock:
    lines: dict
    eta: date = None


