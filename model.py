# from attrs import define
from datetime import date
from typing import Optional, Dict


# @define
class Batch:

    def __init__(self, ref: str, sku: str, qty: int, eta: date):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self.available_quantity = qty

    def allocate(self, line):
        self.available_quantity -= line.qty

    def can_allocate(self, line) -> bool:
        return self.available_quantity >= line.qty


# @define
class OrderLine:

    def __init__(self, order_ref: str, sku: str, qty: int):
        self.orderid = order_ref
        self.sku = sku
        self.qty = qty