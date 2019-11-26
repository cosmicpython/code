from datetime import date
from unittest import mock
import pytest
from allocation import exceptions, messagebus, unit_of_work
from allocation.domain import commands
from allocation.adapters import repository


class FakeRepository(repository.AbstractRepository):

    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)

    def _get_by_batchref(self, batchref):
        return next((
            p for p in self._products for b in p.batches
            if b.reference == batchref
        ), None)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):

    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass



class TestAddBatch:

    @staticmethod
    def test_for_new_product():
        uow = FakeUnitOfWork()
        messagebus.handle(commands.CreateBatch("b1", "CRUNCHY-ARMCHAIR", 100, None), uow)
        assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
        assert uow.committed

    @staticmethod
    def test_for_existing_product():
        uow = FakeUnitOfWork()
        messagebus.handle(commands.CreateBatch("b1", "GARISH-RUG", 100, None), uow)
        messagebus.handle(commands.CreateBatch("b2", "GARISH-RUG", 99, None), uow)
        assert "b2" in [b.reference for b in uow.products.get("GARISH-RUG").batches]



@pytest.fixture(autouse=True)
def fake_redis_publish():
    with mock.patch("allocation.adapters.redis_pubsub.publish"):
        yield


class TestAllocate:

    @staticmethod
    def test_allocates():
        uow = FakeUnitOfWork()
        messagebus.handle(commands.CreateBatch("b1", "COMPLICATED-LAMP", 100, None), uow)
        result = messagebus.handle(commands.Allocate("o1", "COMPLICATED-LAMP", 10), uow)
        assert result == "b1"
        [batch] = uow.products.get("COMPLICATED-LAMP").batches
        assert batch.available_quantity == 90

    @staticmethod
    def test_errors_for_invalid_sku():
        uow = FakeUnitOfWork()
        messagebus.handle(commands.CreateBatch("b1", "AREALSKU", 100, None), uow)

        with pytest.raises(exceptions.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
            messagebus.handle(commands.Allocate("o1", "NONEXISTENTSKU", 10) , uow)

    @staticmethod
    def test_commits():
        uow = FakeUnitOfWork()
        messagebus.handle(commands.CreateBatch("b1", "OMINOUS-MIRROR", 100, None), uow)
        messagebus.handle(commands.Allocate("o1", "OMINOUS-MIRROR", 10), uow)
        assert uow.committed

    @staticmethod
    def test_sends_email_on_out_of_stock_error():
        uow = FakeUnitOfWork()
        messagebus.handle(commands.CreateBatch("b1", "POPULAR-CURTAINS", 9, None), uow)

        with mock.patch("allocation.adapters.email.send") as mock_send_mail:
            messagebus.handle(commands.Allocate("o1", "POPULAR-CURTAINS", 10), uow)
            assert mock_send_mail.call_args == mock.call(
                "stock@made.com",
                f"Out of stock for POPULAR-CURTAINS",
            )


class TestChangeBatchQuantity:

    @staticmethod
    def test_changes_available_quantity():
        uow = FakeUnitOfWork()
        messagebus.handle(commands.CreateBatch("batch1", "ADORABLE-SETTEE", 100, None), uow)
        [batch] = uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch.available_quantity == 100

        messagebus.handle(commands.ChangeBatchQuantity("batch1", 50), uow)

        assert batch.available_quantity == 50


    @staticmethod
    def test_reallocates_if_necessary():
        uow = FakeUnitOfWork()
        messagebus.handle(commands.CreateBatch("batch1", "INDIFFERENT-TABLE", 50, None), uow)
        messagebus.handle(commands.CreateBatch("batch2", "INDIFFERENT-TABLE", 50, date.today()), uow)
        messagebus.handle(commands.Allocate("order1", "INDIFFERENT-TABLE", 20), uow)
        messagebus.handle(commands.Allocate("order2", "INDIFFERENT-TABLE", 20), uow)
        [batch1, batch2] = uow.products.get(sku="INDIFFERENT-TABLE").batches
        assert batch1.available_quantity == 10

        messagebus.handle(commands.ChangeBatchQuantity("batch1", 25), uow)

        # order1 or order2 will be deallocated, so we"ll have 25 - 20 * 1
        assert batch1.available_quantity == 5
        # and 20 will be reallocated to the next batch
        assert batch2.available_quantity == 30
