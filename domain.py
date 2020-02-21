from dataclasses import dataclass
from datetime import date
from typing import List, Optional

@dataclass
class OrderLine:
    sku: str
    qty: int


@dataclass
class Shipment:
    reference: str
    lines: List[OrderLine]
    eta: Optional[date]
    incoterm: str

    def save(self):
        ...
