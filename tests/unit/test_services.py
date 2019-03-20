import pytest
from contextlib import nullcontext

from allocation import model
from allocation import services

class FakeRepository(set):

    def get(self, reference):
        return next(x for x in self if x.reference == reference)

    def list(self):
        return list(self)


class FakeUnitOfWork:
    def __init__(self):
        self.batches = FakeRepository()
        self.committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    line = model.OrderLine('o1', 'sku1', 10)
    batch = model.Batch('b1', 'sku1', 100, eta=None)
    uow = FakeUnitOfWork()
    uow.batches.add(batch)
    start_uow = lambda: nullcontext(uow)
    result = services.allocate(line, start_uow)
    assert result == 'b1'


def test_error_for_invalid_sku():
    line = model.OrderLine('o1', 'nonexistentsku', 10)
    batch = model.Batch('b1', 'actualsku', 100, eta=None)
    uow = FakeUnitOfWork()
    uow.batches.add(batch)
    start_uow = lambda: nullcontext(uow)

    with pytest.raises(services.InvalidSku) as ex:
        services.allocate(line, start_uow)

    assert 'Invalid sku nonexistentsku' in str(ex)


def test_commits():
    line = model.OrderLine('o1', 'sku1', 10)
    batch = model.Batch('b1', 'sku1', 100, eta=None)
    uow = FakeUnitOfWork()
    uow.batches.add(batch)
    start_uow = lambda: nullcontext(uow)

    services.allocate(line, start_uow)
    assert uow.committed is True

