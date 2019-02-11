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
        return {l.sku for l in self.lines}

    @property
    def quantities(self):
        return {l.sku: l.quantity for l in self.lines}




@dataclass
class Order(SkuLines):

    def allocate(self, warehouse, shipments):
        self.allocation = Allocation.for_order(self, warehouse, shipments)
        self.allocation.decrement_source_quantities()


@dataclass
class Warehouse(SkuLines):

    def can_allocate(self, line: OrderLine):
        return line.sku in self.skus and self.quantities[line.sku] > line.quantity

    def decrement_quantity(self, sku, quantity):
        for line in self.lines:
            if line.sku == sku:
                line.quantity -= quantity
                return
        raise Exception(f'sku {sku} not found in warehouse skus ({self.skus})')


@dataclass
class Shipment(Warehouse):
    eta: date = None

    def __lt__(self, other):
        return self.eta < other.eta


@dataclass
class AllocationLine:
    sku: str
    quantity: int
    source: Warehouse

    def decrement_source_quantity(self):
        self.source.decrement_quantity(self.sku, self.quantity)


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
    def for_source(order: Order, source: Warehouse):
        return Allocation(lines=[
            AllocationLine(sku=line.sku, quantity=line.quantity, source=source)
            for line in order.lines
            if source.can_allocate(line)
        ], order=order)

    @staticmethod
    def for_order(order: Order, warehouse: Warehouse, shipments: List[Shipment]):
        allocation = Allocation(lines=[], order=order)
        for source in [warehouse] + sorted(shipments):
            source_allocation = Allocation.for_source(order, source)
            allocation.supplement_with(source_allocation)
        return allocation


    def supplement_with(self, other_allocation):
        self.lines.extend(
            l for l in other_allocation.lines if l.sku not in self.skus
        )

    def decrement_source_quantities(self):
        for line in self.lines:
            line.decrement_source_quantity()


