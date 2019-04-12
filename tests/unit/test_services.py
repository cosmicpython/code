import pytest
from contextlib import nullcontext

from allocation import model
from allocation import services

class FakeRepository(set):

    def get(self, sku):
        try:
            return next(x for x in self if x.sku == sku)
        except StopIteration:
            return None

    def list(self):
        return list(self)


class FakeUnitOfWork:
    def __init__(self):
        self.products = FakeRepository()
        self.committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    product = model.Product(sku='sku1', batches=[model.Batch('b1', 'sku1', 100, eta=None)])
    uow = FakeUnitOfWork()
    uow.products.add(product)
    start_uow = lambda: nullcontext(uow)
    result = services.allocate_(start_uow, 'o1', 'sku1', 10)
    assert result == 'b1'


def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    uow.products.add(model.Product(sku='actualsku', batches=[]))
    uow.products.add(model.Product(sku='othersku', batches=[]))
    start_uow = lambda: nullcontext(uow)

    with pytest.raises(services.InvalidSku) as ex:
        services.allocate_(start_uow, 'o1', 'nonexistentsku', 10)

    assert 'Invalid sku nonexistentsku' in str(ex)


def test_commits():
    uow = FakeUnitOfWork()
    uow.products.add(model.Product(sku='sku1', batches=[
        model.Batch(ref='b1', sku='sku1', qty=100, eta=None),
    ]))
    start_uow = lambda: nullcontext(uow)

    services.allocate_(start_uow, 'o1', 'sku1', 10)
    assert uow.committed is True

