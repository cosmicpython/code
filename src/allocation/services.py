from __future__ import annotations

from allocation.model import OrderLine


class InvalidSku(Exception):
    pass


def allocate(line: OrderLine, start_uow) -> str:
    with start_uow() as uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f'Invalid sku {line.sku}')
        batch = product.allocate(line)
        uow.commit()
    return batch
