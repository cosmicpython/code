import uuid
from datetime import date, timedelta


from domain_model import (
    Line,
    OrderLine,
    Shipment,
    allocate,
)




def random_id():
    return uuid.uuid4().hex[:10]


def test_can_allocate_to_stock():
    order = [OrderLine(sku='a-sku', quantity=10)]
    stock = [Line(sku='a-sku', quantity=1000)]

    allocate(order, stock, shipments=[])

    assert order[0].allocation == 'STOCK'
    assert stock[0].quantity == 990


def test_can_allocate_to_shipment():
    order = [OrderLine(sku='a-sku', quantity=10)]
    shipment = Shipment(id='shipment-id', eta=date.today(), lines={
        'a-sku': 1000
    })

    allocate(order, stock=[], shipments=[shipment])

    assert order[0].allocation == shipment.id
    assert shipment['a-sku'] == 990


def test_ignores_invalid_stock():
    order = [OrderLine(sku='sku1', quantity=10), ]
    stock = [Line(sku='sku2', quantity=1000)]
    shipment = Shipment(id='shipment-id', eta=date.today(), lines={
        'sku1': 1000,
    })

    allocate(order, stock=stock, shipments=[shipment])

    assert order[0].allocation == shipment.id
    assert stock[0].quantity == 1000
    assert shipment['sku1'] == 990


def test_can_allocate_to_correct_shipment():
    order = [OrderLine(sku='sku2', quantity=10)]
    shipment1 = Shipment('shipment1', eta=date.today(), lines={
        'sku1': 1000,
    })
    shipment2 = Shipment('shipment2', eta=date.today(), lines={
        'sku2': 1000,
    })

    allocate(order, stock=[], shipments=[shipment1, shipment2])

    assert order[0].allocation == shipment2.id
    assert shipment1['sku1'] == 1000
    assert shipment2['sku2'] == 990


def test_allocates_to_stock_in_preference_to_shipment():
    order = [OrderLine(sku='sku1', quantity=10)]
    stock = [Line(sku='sku1', quantity=1000)]
    shipment = Shipment('shipment1', eta=date.today(), lines={
        'sku1': 1000,
    })

    allocate(order, stock, shipments=[shipment])

    assert order[0].allocation == 'STOCK'
    assert stock[0].quantity == 990
    assert shipment['sku1'] == 1000


def test_can_allocate_multiple_lines_to_wh():
    order = [
        OrderLine(sku='sku1', quantity=5),
        OrderLine(sku='sku2', quantity=10),
    ]
    stock = [
        Line(sku='sku1', quantity=1000),
        Line(sku='sku2', quantity=1000),
    ]

    allocate(order, stock, shipments=[])
    assert order[0].allocation == 'STOCK'
    assert order[1].allocation == 'STOCK'
    assert stock[0].quantity == 995
    assert stock[1].quantity == 990


def test_can_allocate_multiple_lines_to_shipment():
    order = [
        OrderLine(sku='sku1', quantity=5),
        OrderLine(sku='sku2', quantity=10),
    ]
    shipment = Shipment('shipment1', eta=date.today(), lines={
        'sku1': 1000,
        'sku2': 1000,
    })

    allocate(order, [], shipments=[shipment])

    assert order[0].allocation == shipment.id
    assert order[1].allocation == shipment.id
    assert shipment['sku1'] == 995
    assert shipment['sku2'] == 990


def test_can_allocate_to_both():
    order = [
        OrderLine(sku='sku1', quantity=5),
        OrderLine(sku='sku2', quantity=10),
    ]
    shipment = Shipment('shipment1', eta=date.today(), lines={
        'sku2': 1000,
    })
    stock = [Line(sku='sku1', quantity=1000)]

    allocate(order, stock, shipments=[shipment])

    assert order[0].allocation == 'STOCK'
    assert order[1].allocation == shipment.id
    assert stock[0].quantity == 995
    assert shipment['sku2'] == 990


def test_can_allocate_to_both_preferring_stock():
    order = [
        OrderLine(sku='sku1', quantity=1),
        OrderLine(sku='sku2', quantity=2),
        OrderLine(sku='sku3', quantity=3),
        OrderLine(sku='sku4', quantity=4),
    ]
    shipment = Shipment('shipment1', eta=date.today(), lines={
        'sku1': 1000,
        'sku2': 1000,
        'sku3': 1000,
    })
    stock = [
        Line(sku='sku3', quantity=1000),
        Line(sku='sku4', quantity=1000),
    ]

    allocate(order, stock, shipments=[shipment])

    assert order[0].allocation == shipment.id
    assert order[1].allocation == shipment.id
    assert order[2].allocation == 'STOCK'
    assert order[3].allocation == 'STOCK'
    assert shipment['sku1'] == 999
    assert shipment['sku2'] == 998
    assert shipment['sku3'] == 1000
    assert stock[0].quantity == 997
    assert stock[1].quantity == 996


def test_mixed_allocations_are_avoided_if_possible():
    order = [
        OrderLine(sku='sku1', quantity=10),
        OrderLine(sku='sku2', quantity=10),
    ]
    shipment = Shipment('shipment1', eta=date.today(), lines={
        'sku1': 1000,
        'sku2': 1000,
    })
    stock = [Line(sku='sku1', quantity=1000)]

    allocate(order, stock, shipments=[shipment])

    assert order[0].allocation == shipment.id
    assert order[1].allocation == shipment.id


def test_prefer_allocating_to_earlier_shipment():
    order = [
        OrderLine(sku='sku1', quantity=10),
        OrderLine(sku='sku2', quantity=10),
    ]
    shipment1 = Shipment('shipment1', eta=date.today(), lines={
        'sku1': 1000,
        'sku2': 1000,
    })
    tomorrow = date.today() + timedelta(days=1)
    shipment2 = Shipment('shipment2', eta=tomorrow, lines={
        'sku1': 1000,
        'sku2': 1000,
    })
    stock = []

    allocate(order, stock, shipments=[shipment2, shipment1])

    assert order[0].allocation == shipment1.id
    assert order[1].allocation == shipment1.id


def test_prefer_allocating_to_earlier_even_if_multiple_shipments():
    order = [
        OrderLine(sku='sku1', quantity=10),
        OrderLine(sku='sku2', quantity=10),
        OrderLine(sku='sku3', quantity=10),
    ]
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
    stock = []

    allocate(order, stock, shipments=[shipment3, shipment2, shipment1])

    assert order[1].allocation == shipment2.id
    assert order[2].allocation == shipment2.id


def test_cannot_allocate_if_insufficent_quantity_in_stock():
    order = [OrderLine(sku='a-sku', quantity=10)]
    stock = [Line(sku='a-sku', quantity=5)]

    allocate(order, stock, shipments=[])

    assert order[0].allocation is None


def test_cannot_allocate_if_insufficent_quantity_in_shipment():
    order = [OrderLine(sku='a-sku', quantity=10)]
    shipment = Shipment(id='shipment-id', eta=date.today(), lines={
        'a-sku': 5,
    })

    allocate(order, stock=[], shipments=[shipment])

    assert order[0].allocation is None


def test_cannot_allocate_more_orders_than_we_have_stock_for():
    order1 = [OrderLine(sku='a-sku', quantity=10)]
    order2 = [OrderLine(sku='a-sku', quantity=10)]
    stock = [Line(sku='a-sku', quantity=15)]

    allocate(order1, stock, shipments=[])
    allocate(order2, stock, shipments=[])

    assert order2[0].allocation is None

