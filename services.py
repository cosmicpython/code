from __future__ import annotations

import model
from model import Batch, OrderLine
from repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches) -> bool:
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref

def add_batch(batch: Batch, repo: AbstractRepository, session) -> None:
    repo.add(batch)
    session.commit()

def deallocate(line: OrderLine, repo: AbstractRepository, session):
    batches = repo.list()
    for b in batches:
        if line in b._allocations:
            b.deallocate(line)
            break
    else:
        raise ValueError("Cannot deallocate")   
