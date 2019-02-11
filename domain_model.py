from dataclasses import dataclass

def allocate(order, warehouse, shipments):
    ordered_sources = [warehouse] + sorted(shipments)
    allocation = Allocation(order, {})
    for source in ordered_sources:
        allocation.supplement_with(source.allocation_for(order))
    allocation.decrement_source_quantities()
    return allocation




class Allocation:

    def __init__(self, order, sources):
        self.order = order
        self.sources = sources

    def __getitem__(self, sku):
        return self.sources[sku]

    def __contains__(self, sku):
        return sku in self.sources

    def supplement_with(self, other):
        for sku, qty in other.sources.items():
            if sku not in self:
                self.sources[sku] = qty

    def decrement_source_quantities(self):
        for sku, source in self.sources.items():
            source[sku] -= self.order[sku]


@dataclass
class OrderLine:
    sku: str
    qty: int


class Order:
    def __init__(self, quantities):
        self.quantities = quantities

    def __getitem__(self, sku):
        return self.quantities[sku]

    @property
    def lines(self):
        return [
            OrderLine(sku, qty)
            for sku, qty in self.quantities.items()
        ]


class _Stock(dict):

    def allocation_for(self, order):
        return Allocation(order, {
            line.sku: self
            for line in order.lines
            if line.sku in self
            and self[line.sku] > line.qty
        })


class Warehouse(_Stock):

    def __repr__(self):
        return f'<Warehouse {super().__repr__()}>'



class Shipment(_Stock):
    def __repr__(self):
        return f'<Shipment {super().__repr__()}>'

    def __init__(self, d, eta):
        self.eta = eta
        super().__init__(d)

    def __lt__(self, other):
        return self.eta < other.eta

