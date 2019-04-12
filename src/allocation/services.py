from __future__ import annotations

from datetime import date
from typing import Optional

from allocation.model import Batch, OrderLine, Product


class InvalidSku(Exception):
    pass


def allocate_(start_uow, order_id: str, sku: str, qty: int) -> str:
    line = OrderLine(order_id, sku, qty)
    with start_uow() as uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        batch = product.allocate(line)
        uow.commit()
    return batch


def add_stock(start_uow, ref: str, sku: str, qty: int, eta: Optional[date]=None):
    with start_uow() as uow:
        product = uow.products.get(sku)
        if product is None:
            product = Product(sku)
            uow.products.add(product)
        product.add_batch(ref, qty, eta)
        uow.commit()
