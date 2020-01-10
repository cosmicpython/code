from unittest import mock
import pytest
from allocation.adapters import repository
from allocation.service_layer import services, unit_of_work


class FakeRepository:

    def __init__(self, products):
        self.products = set(products)

    def add(self, product):
        self.products.add(product)

    def get(self, sku):
        return next((p for p in self.products if p.sku == sku), None)



class FakeUnitOfWork:

    def __init__(self):
        self.products = repository.TrackingRepository(FakeRepository([]))
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def commit(self):
        self.committed = True

    def rollback(self):
        pass



def get_uow():
    return unit_of_work.EventPublishingUoW(
        unit_of_work.AutoRollbackUoW(
            FakeUnitOfWork()
        )
    )


def test_add_batch_for_new_product():
    uow = get_uow()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
    assert uow.committed


def test_add_batch_for_existing_product():
    uow = get_uow()
    services.add_batch("b1", "GARISH-RUG", 100, None, uow)
    services.add_batch("b2", "GARISH-RUG", 99, None, uow)
    assert "b2" in [b.reference for b in uow.products.get("GARISH-RUG").batches]


def test_allocate_returns_allocation():
    uow = get_uow()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    uow = get_uow()
    services.add_batch("b1", "AREALSKU", 100, None, uow)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_allocate_commits():
    uow = get_uow()
    services.add_batch("b1", "OMINOUS-MIRROR", 100, None, uow)
    services.allocate("o1", "OMINOUS-MIRROR", 10, uow)
    assert uow.committed


def test_sends_email_on_out_of_stock_error():
    uow = get_uow()
    services.add_batch("b1", "POPULAR-CURTAINS", 9, None, uow)

    with mock.patch("allocation.adapters.email.send_mail") as mock_send_mail:
        services.allocate("o1", "POPULAR-CURTAINS", 10, uow)
        assert mock_send_mail.call_args == mock.call(
            "stock@made.com",
            f"Out of stock for POPULAR-CURTAINS",
        )
