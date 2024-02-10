import datetime
import pytest
import model

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
later = tomorrow + datetime.timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = model.Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = model.Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    line = model.OrderLine("oref", "RETRO-CLOCK", 10)

    model.allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = model.Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=today)
    medium = model.Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = model.Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
    line = model.OrderLine("order1", "MINIMALIST-SPOON", 10)

    model.allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = model.Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = model.Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    line = model.OrderLine("oref", "HIGHBROW-POSTER", 10)
    allocation = model.allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = model.Batch("batch1", "SMALL-FORK", 10, eta=today)
    model.allocate(model.OrderLine("order1", "SMALL-FORK", 10), [batch])

    with pytest.raises(model.OutOfStock, match="SMALL-FORK"):
        model.allocate(model.OrderLine("order2", "SMALL-FORK", 1), [batch])
