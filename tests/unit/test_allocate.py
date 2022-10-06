from datetime import date, timedelta
import pytest
from domain.model import allocate, OrderLine, Batch, OutOfStock

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    line = OrderLine("oref", "RETRO-CLOCK", 10)

    updated_batch = allocate(line, [in_stock_batch, shipment_batch])

    assert updated_batch.ref == in_stock_batch.ref
    assert updated_batch.available_quantity == 90


def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=today)
    medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
    line = OrderLine("order1", "MINIMALIST-SPOON", 10)

    updated_batch = allocate(line, [medium, earliest, latest])

    assert updated_batch.ref == earliest.ref
    assert updated_batch.available_quantity == 90


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-FORK", 10, eta=today)
    updated_batch = allocate(OrderLine("order1", "SMALL-FORK", 10), [batch])
    assert updated_batch

    with pytest.raises(OutOfStock, match="SMALL-FORK"):
        result = allocate(OrderLine("order2", "SMALL-FORK", 1), [updated_batch])
        assert result is None
