from datetime import date, timedelta
import pytest

from model import Batch, OrderLine

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def make_batch_and_line(sku: str, batch_qty: int, line_qty: int):
    return (Batch("1", sku, batch_qty, eta=date.today()),
            OrderLine("order-ref", sku, line_qty))


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, line = make_batch_and_line("TABLE", 20, 2)
    batch.allocate(line)

def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("chair", 20, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("chair", 2, 20)
    assert not small_batch.can_allocate(large_line)


def test_can_allocate_if_available_equal_to_required():
    pytest.fail("todo")


def test_prefers_warehouse_batches_to_shipments():
    pytest.fail("todo")


def test_prefers_earlier_batches():
    pytest.fail("todo")