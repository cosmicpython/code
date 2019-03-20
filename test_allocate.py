from datetime import date, timedelta
from model import allocate, OrderLine, Batch

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)

def test_prefers_warehouse_batches_to_shipments():
    warehouse_batch = Batch('wh-batch', 'sku1', 100, eta=None)
    shipment_batch = Batch('sh-batch', 'sku1', 100, eta=tomorrow)
    line = OrderLine('oref', 'sku1', 10)

    allocate(line, [warehouse_batch, shipment_batch])

    assert warehouse_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch('sh-batch', 'sku1', 100, eta=today)
    medium = Batch('sh-batch', 'sku1', 100, eta=tomorrow)
    latest = Batch('sh-batch', 'sku1', 100, eta=later)
    line = OrderLine('oref', 'sku1', 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_id():
    warehouse_batch = Batch('wh-batch', 'sku1', 100, eta=None)
    shipment_batch = Batch('sh-batch', 'sku1', 100, eta=tomorrow)
    line = OrderLine('oref', 'sku1', 10)
    allocation = allocate(line, [warehouse_batch, shipment_batch])
    assert allocation == 'wh-batch'

