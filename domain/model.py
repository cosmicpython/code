from __future__ import annotations
from dataclasses import dataclass, field, replace
from datetime import date
from typing import Any, Optional, Iterable, List, Set


class OutOfStock(Exception):
    pass


def allocate(line: OrderLine, batches: List[Batch]) -> Optional[Batch]:
    for b in sorted(batches):
        if b.can_allocate(line):
            return b.allocate(line)
    raise OutOfStock(f"Out of stock for sku {line.sku}")


@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


@dataclass(frozen=True)
class Batch:
    ref: str
    sku: str
    _purchased_quantity: int
    eta: Optional[date]
    _allocations: Set[OrderLine] = field(default_factory=set)

    def __repr__(self) -> str:
        return f"<Batch {self.ref}>"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Batch):
            return False
        return other.ref == self.ref

    def __hash__(self) -> int:
        return hash(self.ref)

    def __gt__(self, other: Batch) -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine) -> Optional[Batch]:
        if self.can_allocate(line):
            return replace(self, _allocations=self._allocations | {line})
        return None

    def deallocate(self, line: OrderLine) -> Batch:
        return replace(self, _allocations=self._allocations - {line})

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
