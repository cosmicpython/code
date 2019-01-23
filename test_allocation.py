import uuid
from datetime import date


from domain_model import (
    Allocation,
    Order,
    OrderLine,
    Shipment,
    Stock,
    allocate,
)

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

