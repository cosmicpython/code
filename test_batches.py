# from datetime import date, timedelta
# import pytest

# # from model import ...

# today = date.today()
# tomorrow = today + timedelta(days=1)
# later = tomorrow + timedelta(days=10)

from datetime import date
import datetime
from model import Batch, OrderLine


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine('order-ref', "SMALL-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def make_batch_and_line(sku: str,  batch_qty: int, line_qty: int) -> tuple[Batch, OrderLine]:
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty)
    )


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)

    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_line, large_batch = make_batch_and_line("ELEGANT-LAMP", 2, 20)

    assert small_line.can_allocate(large_batch) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
    different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
    assert batch.can_allocate(different_sku_line) is False


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET",
                                                  20, 2)
    batch.deallocate(unallocated_line)

    assert batch.available_quantity == 20


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 20, 2)

    batch.allocate(line)
    batch.allocate(line)

    assert batch.available_quantity == 18


today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100,
                           eta=tomorrow)

# def test_prefers_warehouse_batches_to_shipments():
#     pytest.fail("todo")


# def test_prefers_earlier_batches():
#     pytest.fail("todo")
