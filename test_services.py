import pytest

import model
import services

class FakeRepository(set):

    def get(self, reference):
        return next(x for x in self if x.reference == reference)

    def list(self):
        return list(self)


class FakeSession():
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    line = model.OrderLine('o1', 'sku1', 10)
    batch = model.Batch('b1', 'sku1', 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == 'b1'


def test_error_for_invalid_sku():
    line = model.OrderLine('o1', 'nonexistentsku', 10)
    batch = model.Batch('b1', 'actualsku', 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku) as ex:
        services.allocate(line, repo, FakeSession())

    assert 'Invalid sku nonexistentsku' in str(ex)


def test_commits():
    line = model.OrderLine('o1', 'sku1', 10)
    batch = model.Batch('b1', 'sku1', 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True

