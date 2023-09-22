# from attrs import define
from datetime import date
from typing import Optional, Dict


# @define
class Batch:

    def __init__(self, ref: str, sku: str, qty: int, eta: date):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._start_quantity = qty
        self._allocations = set()


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
        return self._start_quantity - self.allocated_quantity


    def can_allocate(self, line) -> bool:
        if self.available_quantity < line.qty:
            return False
        elif self.sku != line.sku:
            return False
        return True

# @define
class OrderLine:

    def __init__(self, order_ref: str, sku: str, qty: int):
        self.orderid = order_ref
        self.sku = sku
        self.qty = qty