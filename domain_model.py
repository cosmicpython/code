from dataclasses import dataclass
from datetime import date


def allocate(order, warehouse, shipments):
    ordered_sources = [warehouse] + sorted(shipments)
    allocation = Allocation(order)
    for source in ordered_sources:
        allocation.supplement_with(source.allocation_for(order))
    allocation.decrement_available_quantities()
    return allocation




class Allocation:

    def __init__(self, order):
        self.order = order
        self._sources = {}

    def __getitem__(self, sku):
        return self._sources[sku]

    def __contains__(self, sku):
        return sku in self._sources

    def with_sources(self, sources: dict):
        self._sources = sources
        return self

    def supplement_with(self, other):
        for sku, source in other._sources.items():
            if sku not in self:
                self._sources[sku] = source

    def decrement_available_quantities(self):
        for sku, source in self._sources.items():
            source.decrement_available(sku, self.order[sku])


@dataclass
class Line:
    sku: str
    qty: int


class _Lines:

    def __init__(self, lines: dict):
        self._lines = lines

    def __getitem__(self, sku):
        return self._lines[sku]

    def __contains__(self, sku):
        return sku in self._lines

    @property
    def lines(self):
        return [
            Line(sku, qty)
            for sku, qty in self._lines.items()
        ]


class Order(_Lines):
    pass


class _Stock(_Lines):

    def decrement_available(self, sku, qty):
        self._lines[sku] -= qty

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
