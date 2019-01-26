import uuid
from datetime import date, timedelta


from domain_model import (
    Order,
    Shipment,
    allocate,
)


def random_id():
    return uuid.uuid4().hex[:10]


def test_can_allocate_to_stock():
    order = Order({'a-sku': 10})
    stock = {'a-sku': 1000}

    allocate(order, stock, shipments=[])

    assert order.allocations['a-sku'] == 'STOCK'
    assert stock['a-sku'] == 990


def test_can_allocate_to_shipment():
    order = Order({'a-sku': 10})
    shipment = Shipment(id='shipment-id', eta=date.today(), lines={
        'a-sku': 1000
    })

    allocate(order, stock=[], shipments=[shipment])

    assert order.allocations['a-sku'] == shipment.id
    assert shipment['a-sku'] == 990


def test_ignores_irrelevant_stock():
    order = Order({'sku1': 10})
    stock = {'sku2': 1000}
    shipment = Shipment(id='shipment-id', eta=date.today(), lines={
        'sku1': 1000,
    })

    allocate(order, stock=stock, shipments=[shipment])

    assert order.allocations['sku1'] == shipment.id
    assert stock['sku2'] == 1000
    assert shipment['sku1'] == 990


def test_can_allocate_to_correct_shipment():
    order = Order({'sku2': 10})
    shipment1 = Shipment('shipment1', eta=date.today(), lines={
        'sku1': 1000,
    })
    shipment2 = Shipment('shipment2', eta=date.today(), lines={
        'sku2': 1000,
    })

    allocate(order, stock=[], shipments=[shipment1, shipment2])

    assert order.allocations['sku2'] == shipment2.id
    assert shipment1['sku1'] == 1000
    assert shipment2['sku2'] == 990


def test_allocates_to_stock_in_preference_to_shipment():
    order = Order({'sku1': 10})
    stock = {'sku1': 1000}
    shipment = Shipment('shipment1', eta=date.today(), lines={
        'sku1': 1000,
    })

    allocate(order, stock, shipments=[shipment])

    assert order.allocations['sku1'] == 'STOCK'
    assert stock['sku1'] == 990
    assert shipment['sku1'] == 1000


def test_can_allocate_multiple_lines_to_wh():
    order = Order({'sku1': 5, 'sku2': 10})
    stock = {'sku1': 1000, 'sku2': 1000}

    allocate(order, stock, shipments=[])
    assert order.allocations['sku1'] == 'STOCK'
    assert order.allocations['sku2'] == 'STOCK'
    assert stock['sku1'] == 995
    assert stock['sku2'] == 990


def test_can_allocate_multiple_lines_to_shipment():
    order = Order({'sku1': 5, 'sku2': 10})
    shipment = Shipment('shipment1', eta=date.today(), lines={
        'sku1': 1000,
        'sku2': 1000,
    })

    allocate(order, [], shipments=[shipment])

    assert order.allocations['sku1'] == shipment.id
    assert order.allocations['sku2'] == shipment.id
    assert shipment['sku1'] == 995
    assert shipment['sku2'] == 990


def test_can_allocate_to_both():
    order = Order({'sku1': 5, 'sku2': 10})
    shipment = Shipment('shipment1', eta=date.today(), lines={
        'sku2': 1000,
    })
    stock = {'sku1': 1000}

    allocate(order, stock, shipments=[shipment])

    assert order.allocations['sku1'] == 'STOCK'
    assert order.allocations['sku2'] == shipment.id
    assert stock['sku1'] == 995
    assert shipment['sku2'] == 990


def test_can_allocate_to_both_preferring_stock():
    order = Order({'sku1': 1, 'sku2': 2, 'sku3': 3, 'sku4': 4})
    shipment = Shipment('shipment1', eta=date.today(), lines={
        'sku1': 1000,
        'sku2': 1000,
        'sku3': 1000,
    })
    stock = {'sku3': 1000, 'sku4': 1000}

    allocate(order, stock, shipments=[shipment])

    assert order.allocations['sku1'] == shipment.id
    assert order.allocations['sku2'] == shipment.id
    assert order.allocations['sku3'] == 'STOCK'
    assert order.allocations['sku4'] == 'STOCK'
    assert shipment['sku1'] == 999
    assert shipment['sku2'] == 998
    assert shipment['sku3'] == 1000
    assert stock['sku3'] == 997
    assert stock['sku4'] == 996


def test_mixed_allocations_are_avoided_if_possible():
    order = Order({'sku1': 10, 'sku2': 10})
    shipment = Shipment('shipment1', eta=date.today(), lines={
        'sku1': 1000,
        'sku2': 1000,
    })
    stock = {'sku1': 1000}

    allocate(order, stock, shipments=[shipment])

    assert order.allocations['sku1'] == shipment.id
    assert order.allocations['sku2'] == shipment.id


def test_prefer_allocating_to_earlier_shipment():
    order = Order({'sku1': 10, 'sku2': 10})
    shipment1 = Shipment('shipment1', eta=date.today(), lines={
        'sku1': 1000,
        'sku2': 1000,
    })
    tomorrow = date.today() + timedelta(days=1)
    shipment2 = Shipment('shipment2', eta=tomorrow, lines={
        'sku1': 1000,
        'sku2': 1000,
    })
    stock = {}

    allocate(order, stock, shipments=[shipment2, shipment1])

    assert order.allocations['sku1'] == shipment1.id
    assert order.allocations['sku2'] == shipment1.id


def test_prefer_allocating_to_earlier_even_if_multiple_shipments():
    order = Order({'sku1': 10, 'sku2': 10, 'sku3': 10})
    shipment1 = Shipment(id='shipment1', eta=date.today(), lines={
        'sku1': 1000,
    })
    tomorrow = date.today() + timedelta(days=1)
    shipment2 = Shipment(id='shipment2', eta=tomorrow, lines={
        'sku2': 1000,
        'sku3': 1000,
    })
    later = tomorrow + timedelta(days=1)
    shipment3 = Shipment(id='shipment3', eta=later, lines={
        'sku2': 1000,
        'sku3': 1000,
    })
    stock = {}

    allocate(order, stock, shipments=[shipment3, shipment2, shipment1])

    assert order.allocations['sku1'] == shipment1.id
    assert order.allocations['sku2'] == shipment2.id
    assert order.allocations['sku3'] == shipment2.id


def test_cannot_allocate_if_insufficent_quantity_in_stock():
    order = Order({'a-sku': 10})
    stock = {'a-sku': 5}

    allocate(order, stock, shipments=[])

    assert 'a-sku' not in order.allocations


def test_cannot_allocate_if_insufficent_quantity_in_shipment():
    order = Order({'a-sku': 10})
    shipment = Shipment(id='shipment-id', eta=date.today(), lines={
        'a-sku': 5,
    })

    allocate(order, stock=[], shipments=[shipment])

    assert 'a-sku' not in order.allocations


def test_cannot_allocate_more_orders_than_we_have_stock_for():
    order1 = Order({'a-sku': 10})
    order2 = Order({'a-sku': 10})
    stock = {'a-sku': 15}

    allocate(order1, stock, shipments=[])
    allocate(order2, stock, shipments=[])

    assert 'a-sku' not in order2.allocations

