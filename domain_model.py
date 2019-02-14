from __future__ import annotations
from dataclasses import dataclass
from datetime import date


def allocate(order, warehouse, shipments):
    ordered_sources = [warehouse] + sorted(shipments)
    allocation = Allocation(order)
    for source in ordered_sources:
        allocation.supplement_with(source.allocation_for(order))
    allocation.decrement_available_quantities()
    return allocation


@dataclass(unsafe_hash=True)
class AllocationLine:
    sku: str
    source: _Stock


class Allocation:

    def __init__(self, order):
        self.order = order
        self.lines = []

    def __getitem__(self, sku):
        return next(l.source for l in self.lines if l.sku == sku)

    def __setitem__(self, sku, source):
        line = next(l.source for l in self.lines if l.sku == sku)
        line.source = source

    def __contains__(self, sku):
        return sku in {l.sku for l in self.lines}

    def with_sources(self, sources: dict):
        self.lines = [AllocationLine(sku, source) for sku, source in sources.items()]
        return self

    def supplement_with(self, other: Allocation):
        for line in other.lines:
            if line.sku not in self:
                self.lines.append(line)

    def decrement_available_quantities(self):
        for line in self.lines:
            line.source.decrement_available(line.sku, self.order[line.sku])


@dataclass(unsafe_hash=True)
class Line:
    sku: str
    qty: int


class _Lines:

    def __init__(self, lines: dict):
        self.lines = [Line(sku, qty) for sku, qty in lines.items()]

    def __getitem__(self, sku):
        return next(l.qty for l in self.lines if l.sku == sku)

    def __setitem__(self, sku, qty):
        try:
            line = next(l for l in self.lines if l.sku == sku)
            line.qty = qty
        except StopIteration:
            self.lines.append(Line(sku=sku, qty=qty))

    def __contains__(self, sku):
        return sku in {l.sku for l in self.lines}



class Order(_Lines):
    pass


class _Stock(_Lines):

    def decrement_available(self, sku, qty):
        self[sku] -= qty

    def allocation_for(self, order: Order):
        return Allocation(order).with_sources({
            line.sku: self
            for line in order.lines
            if line.sku in self
            and self[line.sku] > line.qty
        })


class Warehouse(_Stock):

    def __repr__(self):
        return f'<Warehouse lines={self._lines}>'



class Shipment(_Stock):

    def __init__(self, lines: dict, eta: date):
        self.eta = eta
        super().__init__(lines)

    def __repr__(self):
        return f'<Shipment eta={self.eta} lines={self._lines}>'

    def __lt__(self, other):
        return self.eta < other.eta
