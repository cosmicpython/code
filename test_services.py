from unittest.mock import Mock

from pytest import raises

import model
from services import allocate, InvalidSku
from repository import AbstractRepository


class FakeRepository(AbstractRepository):
    def __init__(self):
        self.items = []

    def add(self, batch):
        self.items.append(batch)

    def get(self, reference):
        res = [item for item in self.items if item.reference == reference]
        if not res:
            return None
        return res[0]

    def list(self):
        return self.items


def test_allocate_allocated():
    session = Mock()
    rep = FakeRepository()
    rep.add(model.Batch(ref='batch1', sku='SKU2', qty=10, eta=None))
    rep.add(model.Batch(ref='batch2', sku='SKU1', qty=10, eta=None))
    order_line = model.OrderLine(orderid='order1', sku='SKU1', qty=10)
    assert allocate(order_line=order_line, rep=rep, session=session) == 'batch2'
    session.commit.assert_called_once()


def test_allocate_wrong_sku():
    session = Mock()
    rep = FakeRepository()
    rep.add(model.Batch(ref='batch1', sku='SKU1', qty=10, eta=None))
    order_line = model.OrderLine(orderid='order1', sku='SKU2', qty=10)
    with raises(InvalidSku):
        allocate(order_line=order_line, rep=rep, session=session)
