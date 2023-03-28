from dataclasses import dataclass
from typing import Optional, List
from datetime import date


class OutOfStock(Exception):
    pass



@dataclass(frozen=True)
class OrderLine:
    order_id: int
    sku: str
    quantity: int

class Batch:
    def __init__(self, reference: str, sku: str, quantity: int,  eta: Optional[date]) -> None:
        """
        Batch constructor
        """
        self.reference = reference
        self.sku =  sku
        self.eta = eta
        self.quantity = quantity

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        """ 
        update the  current quantity available from batch
        """
        if self.can_allocate(line):
            self.quantity -= line.quantity

    
    def can_allocate(self,  line: OrderLine):
        """
        Check if the batch have stock available

        Returns:
            Boolean: validation result
        """
        return line.quantity <= self.quantity

def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
