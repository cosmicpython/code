from datetime import date, timedelta
import pytest

from model import OrderLine, Batch, allocate

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch('ref-001', 'sku-001', 34, None)
    line = OrderLine('ord-001', 'sku-001', 15)
    batch.allocate(line)
    assert batch.quantity == 19

def test_can_allocate_if_available_greater_than_required():
    batch = Batch('ref-001', 'sku-001', 34, None)
    line = OrderLine('ord-001', 'sku-001', 36)
    batch.allocate(line)
    assert batch.quantity == 34

def test_cannot_allocate_if_available_smaller_than_required():
    batch = Batch('ref-001', 'sku-001', 34, None)
    line = OrderLine('ord-001', 'sku-001', 36)
    assert batch.can_allocate(line) == False


def test_can_allocate_if_available_equal_to_required():
    batch = Batch('ref-001', 'sku-001', 34, None)
    line = OrderLine('ord-001', 'sku-001', 30)
    assert batch.can_allocate(line)

def test_prefers_warehouse_batches_to_shipments():
    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=None)
    medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
    line = OrderLine("order1", "MINIMALIST-SPOON", 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.quantity == 90
    assert medium.quantity == 100
    assert latest.quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=today)
    medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
    line = OrderLine("order1", "MINIMALIST-SPOON", 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.quantity == 90
    assert medium.quantity == 100
    assert latest.quantity == 100
