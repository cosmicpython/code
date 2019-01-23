import uuid
from datetime import date


from domain_model import (
    Allocation,
    Order,
    OrderLine,
    Shipment,
    Stock,
    allocate as allocate_
)


allocate = lambda *a, **kw: list(allocate_(*a, **kw))


def random_id():
    return uuid.uuid4().hex[:10]


def test_can_allocate_to_warehouse_stock():
    sku = random_id()
    order = Order(id=random_id(), lines=[
        OrderLine(sku=sku, quantity=10),
    ])
    stock = Stock(sku=sku, quantity=1000)

    allocations = allocate(order, [stock], shipments=[])

    assert allocations[0].order_id == order.id
    assert allocations[0].sku == sku
    assert allocations[0].shipment_id is None
    assert allocations[0].quantity == 10


def test_can_allocate_to_shipment():
    sku = random_id()
    order = Order(id=random_id(), lines=[
        OrderLine(sku=sku, quantity=10),
    ])
    shipment = Shipment(id=random_id(), eta=date.today(), lines=[
        OrderLine(sku=sku, quantity=1000),
    ])

    allocations = allocate(order, stock=[], shipments=[shipment])

    assert allocations[0].order_id == order.id
    assert allocations[0].sku == sku
    assert allocations[0].shipment_id == shipment.id
    assert allocations[0].quantity == 10


def test_ignores_invalid_stock():
    sku1, sku2 = random_id(), random_id()
    order = Order(id=random_id(), lines=[
        OrderLine(sku=sku1, quantity=10),
    ])
    stock = Stock(sku=sku2, quantity=1000)
    shipment = Shipment(id=random_id(), eta=date.today(), lines=[
        OrderLine(sku=sku1, quantity=1000),
    ])

    allocations = allocate(order, stock=[stock], shipments=[shipment])

    assert allocations[0].order_id == order.id
    assert allocations[0].sku == sku1
    assert allocations[0].shipment_id == shipment.id
    assert allocations[0].quantity == 10


def test_can_allocate_to_correct_shipment():
    sku1, sku2 = random_id(), random_id()
    order = Order(id=random_id(), lines=[
        OrderLine(sku=sku2, quantity=10),
    ])
    shipment1 = Shipment(id=random_id(), eta=date.today(), lines=[
        OrderLine(sku=sku1, quantity=1000),
    ])
    shipment2 = Shipment(id=random_id(), eta=date.today(), lines=[
        OrderLine(sku=sku2, quantity=1000),
    ])

    allocations = allocate(order, stock=[], shipments=[shipment1, shipment2])

    assert allocations[0].order_id == order.id
    assert allocations[0].sku == sku2
    assert allocations[0].shipment_id == shipment2.id
    assert allocations[0].quantity == 10


def test_allocates_to_warehouse_stock_in_preference_to_shipment():
    sku = random_id()
    order = Order(id=random_id(), lines=[
        OrderLine(sku=sku, quantity=10),
    ])
    stock = Stock(sku=sku, quantity=1000)
    shipment = Shipment(id=random_id(), eta=date.today(), lines=[
        OrderLine(sku=sku, quantity=1000),
    ])

    allocations = allocate(order, [stock], shipments=[shipment])

    assert allocations[0].order_id == order.id
    assert allocations[0].sku == sku
    assert allocations[0].shipment_id is None
    assert allocations[0].quantity == 10


def test_can_allocate_multiple_lines_to_wh():
    sku1, sku2 = random_id(), random_id()
    order = Order(id=random_id(), lines=[
        OrderLine(sku=sku1, quantity=10),
        OrderLine(sku=sku2, quantity=10),
    ])
    stock = [
        Stock(sku=sku1, quantity=1000),
        Stock(sku=sku2, quantity=1000),
    ]

    allocations = allocate(order, stock, shipments=[])
    assert Allocation(order.id, sku1, 10, shipment_id=None) in allocations
    assert Allocation(order.id, sku2, 10, shipment_id=None) in allocations


def test_can_allocate_multiple_lines_to_shipment():
    sku1, sku2 = random_id(), random_id()
    order = Order(id=random_id(), lines=[
        OrderLine(sku=sku1, quantity=10),
        OrderLine(sku=sku2, quantity=10),
    ])
    shipment = Shipment(id=random_id(), eta=date.today(), lines=[
        OrderLine(sku=sku1, quantity=1000),
        OrderLine(sku=sku2, quantity=1000),
    ])

    allocations = allocate(order, [], shipments=[shipment])
    assert Allocation(order.id, sku1, 10, shipment_id=shipment.id) in allocations
    assert Allocation(order.id, sku2, 10, shipment_id=shipment.id) in allocations


def test_can_allocate_to_both():
    sku1, sku2 = random_id(), random_id()
    order = Order(id=random_id(), lines=[
        OrderLine(sku=sku1, quantity=10),
        OrderLine(sku=sku2, quantity=10),
    ])
    shipment = Shipment(id=random_id(), eta=date.today(), lines=[
        OrderLine(sku=sku2, quantity=1000),
    ])
    stock = [
        Stock(sku=sku1, quantity=1000),
    ]

    allocations = allocate(order, stock, shipments=[shipment])
    assert Allocation(order.id, sku1, 10, shipment_id=None) in allocations
    assert Allocation(order.id, sku2, 10, shipment_id=shipment.id) in allocations


def test_can_allocate_to_both_preferring_stock():
    sku1, sku2, sku3, sku4 = [random_id() for _ in range(4)]
    order = Order(id=random_id(), lines=[
        OrderLine(sku=sku1, quantity=10),
        OrderLine(sku=sku2, quantity=10),
        OrderLine(sku=sku3, quantity=10),
        OrderLine(sku=sku4, quantity=10),
    ])
    shipment = Shipment(id=random_id(), eta=date.today(), lines=[
        OrderLine(sku=sku1, quantity=1000),
        OrderLine(sku=sku2, quantity=1000),
        OrderLine(sku=sku3, quantity=1000),
    ])
    stock = [
        Stock(sku=sku3, quantity=1000),
        Stock(sku=sku4, quantity=1000),
    ]

    allocations = allocate(order, stock, shipments=[shipment])
    assert Allocation(order.id, sku1, 10, shipment_id=shipment.id) in allocations
    assert Allocation(order.id, sku2, 10, shipment_id=shipment.id) in allocations
    assert Allocation(order.id, sku3, 10, shipment_id=None) in allocations
    assert Allocation(order.id, sku4, 10, shipment_id=None) in allocations
    assert Allocation(order.id, sku3, 10, shipment_id=shipment.id) not in allocations


