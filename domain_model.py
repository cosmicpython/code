from dataclasses import dataclass
from typing import List
from datetime import date

@dataclass
class OrderLine:
    sku: str
    quantity: int



@dataclass
class SkuLines:
    lines: List[OrderLine]

    @property
    def skus(self):
        return set(l.sku for l in self.lines)

    @property
    def quantities(self):
        return {l.sku: l.quantity for l in self.lines}




@dataclass
class Order(SkuLines):

    @property
    def fully_allocated(self):
        return self.allocation.is_complete

    def allocate(self, stock, shipments):
        self.allocation = Allocation(lines=[], order=self)
        for source in [stock] + sorted(shipments):
            source_allocation = Allocation.for_(self, source)
            if source_allocation.is_complete:
                self.allocation = source_allocation
                self.allocation.apply()
                return
            self.allocation.supplement_with(source_allocation)
        self.allocation.apply()



@dataclass
class Stock(SkuLines):

    def can_allocate(self, line: OrderLine):
        return line.sku in self.skus and self.quantities[line.sku] > line.quantity

    def allocate(self, sku, quantity):
        for line in self.lines:
            if line.sku == sku:
                line.quantity -= quantity
                return
        raise Exception(f'sku {sku} not found in stock skus ({self.skus})')


@dataclass
class Shipment(Stock):
    eta: date = None

    def __lt__(self, other):
        return self.eta < other.eta


@dataclass
class AllocationLine:
    sku: str
    source: Stock


@dataclass
class Allocation:
    lines: List[AllocationLine]
    order: Order

    @property
    def skus(self):
        return set(l.sku for l in self.lines)

    @property
    def sources(self):
        return {l.sku: l.source for l in self.lines}

    @staticmethod
    def for_(order: Order, source: Stock):
        return Allocation(
            lines=[
                AllocationLine(sku=line.sku, source=source) for line in order.lines
                if source.can_allocate(line)
            ],
            order=order
        )

    def supplement_with(self, allocation):
        for line in allocation.lines:
            if line.sku in self.skus:
                continue
            self.lines.append(line)

    @property
    def is_complete(self):
        return self.skus == self.order.skus

    def apply(self):
        for line in self.lines:
            line.source.allocate(line.sku, self.order.quantities[line.sku])

