from datetime import date, timedelta
import pytest

from allocation.model import allocate, Product, OrderLine, Batch, OutOfStock

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)

def test_prefers_warehouse_batches_to_shipments():
    warehouse_batch = Batch('wh-batch', 'sku1', 100, eta=None)
    shipment_batch = Batch('sh-batch', 'sku1', 100, eta=tomorrow)
    product = Product(sku='sku1', batches=[warehouse_batch, shipment_batch])
    line = OrderLine('oref', 'sku1', 10)

    product.allocate(line)

    assert warehouse_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch('sh-batch', 'sku1', 100, eta=today)
    medium = Batch('sh-batch', 'sku1', 100, eta=tomorrow)
    latest = Batch('sh-batch', 'sku1', 100, eta=later)
    product = Product(sku='sku1', batches=[medium, earliest, latest])
    line = OrderLine('oref', 'sku1', 10)

    product.allocate(line)

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_id():
    warehouse_batch = Batch('wh-batch', 'sku1', 100, eta=None)
    shipment_batch = Batch('sh-batch', 'sku1', 100, eta=tomorrow)
    line = OrderLine('oref', 'sku1', 10)
    product = Product(sku='sku1', batches=[warehouse_batch, shipment_batch])
    allocation = product.allocate(line, )
    assert allocation == 'wh-batch'


def test_raises_out_of_stock_exception_if_cannot_allocate():
    sku1_batch = Batch('batch1', 'sku1', 100, eta=today)
    sku2_line = OrderLine('oref', 'sku2', 10)
    product = Product(sku='sku1', batches=[sku1_batch])

    with pytest.raises(OutOfStock) as ex:
        product.allocate(sku2_line)
    assert 'sku2' in str(ex)

