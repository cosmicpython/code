from datetime import date
from unittest import mock
import pytest
from allocation import commands, exceptions, messagebus, repository, unit_of_work
from .fakes import FakeBus


class TestAddBatch:

    @staticmethod
    def test_for_new_product():
        bus = FakeBus()
        bus.handle([commands.CreateBatch("b1", "CRUNCHY-ARMCHAIR", 100, None)])
        assert bus.uow.products.get("CRUNCHY-ARMCHAIR") is not None
        assert bus.uow.committed

    @staticmethod
    def test_for_existing_product():
        bus = FakeBus()
        bus.handle([
            commands.CreateBatch("b1", "GARISH-RUG", 100, None),
            commands.CreateBatch("b2", "GARISH-RUG", 99, None),
        ])
        assert "b2" in [b.reference for b in bus.uow.products.get("GARISH-RUG").batches]



class TestAllocate:

    @staticmethod
    def test_allocates():
        bus = FakeBus()
        bus.handle([
            commands.CreateBatch("b1", "COMPLICATED-LAMP", 100, None),
            commands.Allocate("o1", "COMPLICATED-LAMP", 10),
        ])
        [batch] = bus.uow.products.get("COMPLICATED-LAMP").batches
        assert batch.available_quantity == 90

    @staticmethod
    def test_errors_for_invalid_sku():
        bus = FakeBus()
        bus.handle([commands.CreateBatch("b1", "AREALSKU", 100, None)])

        with pytest.raises(exceptions.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
            bus.handle([
                commands.Allocate("o1", "NONEXISTENTSKU", 10)
            ])

    @staticmethod
    def test_commits():
        bus = FakeBus()
        bus.handle([
            commands.CreateBatch("b1", "OMINOUS-MIRROR", 100, None),
            commands.Allocate("o1", "OMINOUS-MIRROR", 10),
        ])
        assert bus.uow.committed

    @staticmethod
    def test_sends_email_on_out_of_stock_error():
        bus = FakeBus()
        bus.handle([
            commands.CreateBatch("b1", "POPULAR-CURTAINS", 9, None),
            commands.Allocate("o1", "POPULAR-CURTAINS", 10),
        ])
        assert bus.dependencies['notifications'].sent['stock@made.com'] == [
            f"Out of stock for POPULAR-CURTAINS",
        ]


class TestChangeBatchQuantity:

    @staticmethod
    def test_changes_available_quantity():
        bus = FakeBus()
        bus.handle([commands.CreateBatch("b1", "ADORABLE-SETTEE", 100, None)])
        [batch] = bus.uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch.available_quantity == 100

        bus.handle([commands.ChangeBatchQuantity("b1", 50)])
        assert batch.available_quantity == 50


    @staticmethod
    def test_reallocates_if_necessary():
        bus = FakeBus()
        bus.handle([
            commands.CreateBatch("b1", "INDIFFERENT-TABLE", 50, None),
            commands.CreateBatch("b2", "INDIFFERENT-TABLE", 50, date.today()),
            commands.Allocate("o1", "INDIFFERENT-TABLE", 20),
            commands.Allocate("o2", "INDIFFERENT-TABLE", 20),
        ])
        [batch1, batch2] = bus.uow.products.get(sku="INDIFFERENT-TABLE").batches
        assert batch1.available_quantity == 10

        bus.handle([commands.ChangeBatchQuantity("b1", 25)])

        # o1 or o2 will be deallocated, so we"ll have 25 - 20 * 1
        assert batch1.available_quantity == 5
        # and 20 will be reallocated to the next batch
        assert batch2.available_quantity == 30
