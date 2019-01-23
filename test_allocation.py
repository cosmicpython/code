import uuid
from domain_model import (
    Allocation,
    Order,
    OrderLine,
    Stock,
    allocate,
)

def random_id():
    return uuid.uuid4().hex


def test_allocates_to_warehouse_stock_if_available():
    sku = random_id()
    order = Order(id=random_id(), lines=[
        OrderLine(sku=sku, quantity=10)
    ])
    stock = Stock(
        sku=sku,
        quantity=1000
    )

    allocations = allocate(order, stock, shipments=[])

    assert allocations[0].order_id == order.id
    assert allocations[0].sku == sku
    assert allocations[0].shipment_id is None
    assert allocations[0].quantity == 10



