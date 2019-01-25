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
    sku = random_id()
    order = [OrderLine(sku=sku, quantity=10)]
    stock = [Line(sku=sku, quantity=1000)]

    allocate(order, stock, shipments=[])

    assert order[0].allocation == 'STOCK'


def test_can_allocate_to_shipment():
    sku = random_id()
    order = [OrderLine(sku=sku, quantity=10)]
    shipment = Shipment(id=random_id(), eta=date.today(), lines=[
        Line(sku=sku, quantity=1000),
    ])

    allocate(order, stock=[], shipments=[shipment])

    assert order[0].allocation == shipment.id


def test_ignores_invalid_stock():
    sku1, sku2 = random_id(), random_id()
    order = [OrderLine(sku=sku1, quantity=10), ]
    stock = [Line(sku=sku2, quantity=1000)]
    shipment = Shipment(id=random_id(), eta=date.today(), lines=[
        Line(sku=sku1, quantity=1000),
    ])

    allocate(order, stock=stock, shipments=[shipment])

    assert order[0].allocation == shipment.id


def test_can_allocate_to_correct_shipment():
    sku1, sku2 = random_id(), random_id()
    order = [OrderLine(sku=sku2, quantity=10)]
    shipment1 = Shipment(id=random_id(), eta=date.today(), lines=[
        Line(sku=sku1, quantity=1000),
    ])
    shipment2 = Shipment(id=random_id(), eta=date.today(), lines=[
        Line(sku=sku2, quantity=1000),
    ])

    allocate(order, stock=[], shipments=[shipment1, shipment2])

    assert order[0].allocation == shipment2.id


def test_allocates_to_stock_in_preference_to_shipment():
    sku = random_id()
    order = [OrderLine(sku=sku, quantity=10)]
    stock = [Line(sku=sku, quantity=1000)]
    shipment = Shipment(id=random_id(), eta=date.today(), lines=[
        Line(sku=sku, quantity=1000),
    ])

    allocate(order, stock, shipments=[shipment])

    assert order[0].allocation == 'STOCK'


def test_can_allocate_multiple_lines_to_wh():
    sku1, sku2 = random_id(), random_id()
    order = [
        OrderLine(sku=sku1, quantity=10),
        OrderLine(sku=sku2, quantity=10),
    ]
    stock = [
        Line(sku=sku1, quantity=1000),
        Line(sku=sku2, quantity=1000),
    ]

    allocate(order, stock, shipments=[])
    assert order[0].allocation == 'STOCK'
    assert order[1].allocation == 'STOCK'


def test_can_allocate_multiple_lines_to_shipment():
    sku1, sku2 = random_id(), random_id()
    order = [
        OrderLine(sku=sku1, quantity=10),
        OrderLine(sku=sku2, quantity=10),
    ]
    shipment = Shipment(id=random_id(), eta=date.today(), lines=[
        Line(sku=sku1, quantity=1000),
        Line(sku=sku2, quantity=1000),
    ])

    allocate(order, [], shipments=[shipment])

    assert order[0].allocation == shipment.id
    assert order[1].allocation == shipment.id


def test_can_allocate_to_both():
    sku1, sku2 = random_id(), random_id()
    order = [
        OrderLine(sku=sku1, quantity=10),
        OrderLine(sku=sku2, quantity=10),
    ]
    shipment = Shipment(id=random_id(), eta=date.today(), lines=[
        Line(sku=sku2, quantity=1000),
    ])
    stock = [Line(sku=sku1, quantity=1000)]

    allocate(order, stock, shipments=[shipment])

    assert order[0].allocation == 'STOCK'
    assert order[1].allocation == shipment.id


def test_can_allocate_to_both_preferring_stock():
    sku1, sku2, sku3, sku4 = [random_id() for _ in range(4)]
    order = [
        OrderLine(sku=sku1, quantity=10),
        OrderLine(sku=sku2, quantity=10),
        OrderLine(sku=sku3, quantity=10),
        OrderLine(sku=sku4, quantity=10),
    ]
    shipment = Shipment(id=random_id(), eta=date.today(), lines=[
        Line(sku=sku1, quantity=1000),
        Line(sku=sku2, quantity=1000),
        Line(sku=sku3, quantity=1000),
    ])
    stock = [
        Line(sku=sku3, quantity=1000),
        Line(sku=sku4, quantity=1000),
    ]

    allocate(order, stock, shipments=[shipment])

    assert order[0].allocation == shipment.id
    assert order[1].allocation == shipment.id
    assert order[2].allocation == 'STOCK'
    assert order[3].allocation == 'STOCK'


def test_mixed_allocations_are_avoided_if_possible():
    sku1, sku2 = random_id(), random_id()
    order = [
        OrderLine(sku=sku1, quantity=10),
        OrderLine(sku=sku2, quantity=10),
    ]
    shipment = Shipment(id=random_id(), eta=date.today(), lines=[
        Line(sku=sku1, quantity=1000),
        Line(sku=sku2, quantity=1000),
    ])
    stock = [Line(sku=sku1, quantity=1000)]

    allocate(order, stock, shipments=[shipment])

    assert order[0].allocation == shipment.id
    assert order[1].allocation == shipment.id


def test_prefer_allocating_to_earlier_shipment():
    sku1, sku2 = random_id(), random_id()
    order = [
        OrderLine(sku=sku1, quantity=10),
        OrderLine(sku=sku2, quantity=10),
    ]
    shipment1 = Shipment(id=random_id(), eta=date.today(), lines=[
        Line(sku=sku1, quantity=1000),
        Line(sku=sku2, quantity=1000),
    ])
    tomorrow = date.today() + timedelta(days=1)
    shipment2 = Shipment(id=random_id(), eta=tomorrow, lines=[
        Line(sku=sku1, quantity=1000),
        Line(sku=sku2, quantity=1000),
    ])
    stock = []

    allocate(order, stock, shipments=[shipment2, shipment1])

    assert order[0].allocation == shipment1.id
    assert order[1].allocation == shipment1.id


def test_prefer_allocating_to_earlier_even_if_multiple_shipments():
    sku1, sku2, sku3 = random_id(), random_id(), random_id()
    order = [
        OrderLine(sku=sku1, quantity=10),
        OrderLine(sku=sku2, quantity=10),
        OrderLine(sku=sku3, quantity=10),
    ]
    shipment1 = Shipment(id=random_id(), eta=date.today(), lines=[
        Line(sku=sku1, quantity=1000),
    ])
    tomorrow = date.today() + timedelta(days=1)
    shipment2 = Shipment(id=random_id(), eta=tomorrow, lines=[
        Line(sku=sku2, quantity=1000),
        Line(sku=sku3, quantity=1000),
    ])
    later = tomorrow + timedelta(days=1)
    shipment3 = Shipment(id=random_id(), eta=later, lines=[
        Line(sku=sku2, quantity=1000),
        Line(sku=sku3, quantity=1000),
    ])
    stock = []

    allocate(order, stock, shipments=[shipment3, shipment2, shipment1])

    assert order[1].allocation == shipment2.id
    assert order[2].allocation == shipment2.id

