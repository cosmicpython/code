from __future__ import annotations
import dataclasses
import datetime
import typing

OrderReference = typing.NewType("OrderReference", str)
Quantity = typing.NewType("Quantity", int)
Sku = typing.NewType("Sku", str)
Reference = typing.NewType("Reference", str)


class OutOfStock(Exception):
    pass


def allocate(line: OrderLine, batches: typing.List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")


@dataclasses.dataclass(frozen=True)
class OrderLine:
    orderid: OrderReference
    sku: Sku
    qty: Quantity


class Batch:
    def __init__(self, ref: Reference, sku: Sku, qty: Quantity, eta: typing.Optional[datetime.date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations = set()  # type: typing.Set[OrderLine]

    def __repr__(self):
        return f"<Batch {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
