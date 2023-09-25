from datetime import date, timedelta
import pytest

from model import allocate, Batch, OrderLine, OutOfStock

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def make_batch_and_line(sku: str, batch_qty: int, line_qty: int):
    return (
        Batch("1", sku, batch_qty, eta=None),
        OrderLine("order-ref", sku, line_qty),
    )


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, line = make_batch_and_line("TABLE", 20, 2)
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("CHAIR", 20, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("CHAIR", 2, 20)
    assert not small_batch.can_allocate(large_line)


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("CHAIR", 20, 20)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_dont_match():
    batch, line = make_batch_and_line("CHAIR", 20, 20)
    line.sku = "DESK"
    assert not batch.can_allocate(line)


def test_can_deallocate():
    batch, line = make_batch_and_line("TABLE", 20, 2)
    batch.allocate(line)
    batch.deallocate(line)
    assert batch.available_quantity == 20


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("TRINKET", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("TABLE", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_batch_is_self_after_eta_change():
    batch = Batch("1", "foo", 20, today)
    delayed_batch = batch
    delayed_batch.eta = tomorrow
    assert batch is delayed_batch


def test_prefers_in_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "CLOCK", 100, eta=today)
    line = OrderLine("oref", "CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "TARDIS", 100, eta=today)
    medium = Batch("normal-batch", "TARDIS", 100, eta=tomorrow)
    latest = Batch("slow-batch", "TARDIS", 100, eta=later)
    line = OrderLine("oref", "TARDIS", 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_allocate_returns_batch_ref():
    in_stock_batch = Batch("in-stock-batch", "CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "CLOCK", 100, eta=today)
    line = OrderLine("oref", "CLOCK", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == "in-stock-batch"


def test_allocate_raises_out_of_stock_exception():
    batch = Batch("batch1", "SMALL-TABLE", 10, eta=tomorrow)
    line = OrderLine("order1", "SMALL-TABLE", 10)

    with pytest.raises(OutOfStock, match="SMALL-TABLE"):
        allocate(line, [batch])
