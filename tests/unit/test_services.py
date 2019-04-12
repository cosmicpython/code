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

    def reset(self):
        self.committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    uow = FakeUnitOfWork()
    start_uow = lambda: nullcontext(uow)

    services.add_stock(start_uow, 'b1', 'sku1', 100)
    result = services.allocate_(start_uow, 'o1', 'sku1', 10)
    assert result == 'b1'


def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    start_uow = lambda: nullcontext(uow)

    with pytest.raises(services.InvalidSku) as ex:
        services.allocate_(start_uow, 'o1', 'nonexistentsku', 10)

    assert 'Invalid sku nonexistentsku' in str(ex)


def test_commits():
    uow = FakeUnitOfWork()
    start_uow = lambda: nullcontext(uow)

    services.add_stock(start_uow, 'b1', 'sku1', 100)
    uow.reset()

    services.allocate_(start_uow, 'o1', 'sku1', 10)
    assert uow.committed is True
