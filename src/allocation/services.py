from __future__ import annotations

from datetime import date
from typing import Optional

from allocation.model import Batch, OrderLine


class InvalidSku(Exception):
    pass


def allocate_(start_uow, order_id: str, sku: str, qty: int) -> str:
    line = OrderLine(order_id, sku, qty)
    return allocate(line, start_uow)

def allocate(line: OrderLine, start_uow) -> str:
    with start_uow() as uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        batch = product.allocate(line)
        uow.commit()
    return batch
