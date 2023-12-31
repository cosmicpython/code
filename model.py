from dataclasses import dataclass
from datetime import date
from typing import Optional


class OutOfStock(Exception):
    pass


@dataclass(frozen=True)
class OrderLine:
    """
    Class OrderLine:

    +--------------------------+
    |       OrderLine          |
    +--------------------------+
    | - orderid: str           |
    | - sku: str               |
    | - qty: int               |
    +--------------------------+
    """
    order_id: str
    sku: str
    qty: int


class Batch:
    """
    Class Batch:

    +-------------------------+
    |        Batch            |
    +-------------------------+
    | - reference: str        |
    | - sku: str              |
    | - eta: datetime         |
    | - _purchased_quantity   |
    | - _allocations: Set     |
    +-------------------------+
    | + allocate(order_line)  |
    | + deallocate(order_line)|
    | + available_quantity()  |
    +-------------------------+
    """

    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]) -> None:
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations: set[OrderLine] = set()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Batch):
            return False

        return other.reference == self.reference

    def __hash__(self) -> int:
        return hash(self.reference)

    def __gt__(self, other: 'Batch'):
        if self.eta is None:
            return False
        if other.eta is None:
            return True

        return self.eta > other.eta

    def allocate(self, line: OrderLine) -> None:
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


def allocate(line: OrderLine, batches: list[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration as error:
        raise OutOfStock(f"Out of stock for sku {line.sku}") from error
