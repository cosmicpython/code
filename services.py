from __future__ import annotations
from sqlalchemy.orm import Session

import model
from repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(order_line: model.OrderLine, batches: list[model.Batch]):
    return any(batch.sku == order_line.sku for batch in batches)


def allocate(order_line: model.OrderLine, rep: AbstractRepository, session: Session):
    batches = rep.list()
    if not is_valid_sku(order_line, batches):
        raise InvalidSku(f'Invalid sku {order_line.sku}')
    batchref = model.allocate(order_line, batches)
    session.commit()
    return batchref