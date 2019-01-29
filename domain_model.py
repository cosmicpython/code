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
            self.allocations.update({
                key: stock
                for key in self.lines
                if key in source.lines
            })
            if self.fully_allocated:
                return


@dataclass
class Stock:
    lines: dict
    eta: date = None


