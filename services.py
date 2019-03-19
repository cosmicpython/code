from __future__ import annotations

import model
from model import OrderLine
from repository import BatchRepository

class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}

def allocate(line: OrderLine, repo: BatchRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f'Invalid sku {line.sku}')
    batch = model.allocate(line, batches)
    session.commit()
    return batch

