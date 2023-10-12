from datetime import date

class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: date):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._initial_quantity = qty
        self._allocations = set()  # set[OrderLine]

    def allocate(self, line) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self):
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self):
        return self._initial_quantity - self.allocated_quantity

    def can_allocate(self, line) -> bool:
        if self.available_quantity < line.qty:
            return False
        elif self.sku != line.sku:
            return False
        elif self.eta and self.eta > date.today():
            return False
        return True

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __lt__(self, other):
        if not isinstance(other, Batch):
            return False
        if not self.eta:
            return True
        if not other.eta:
            return False
        return self.eta < other.eta

    def __hash__(self):
        return hash(self.reference)


class OrderLine:
    def __init__(self, order_ref: str, sku: str, qty: int):
        self.orderid = order_ref
        self.sku = sku
        self.qty = qty


class OutOfStock(Exception):
    pass


def allocate(line: OrderLine, batches: list[Batch]) -> Optional[str]:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
