import pytest
from allocation import model
from allocation import unit_of_work

def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    session.execute(
        'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
        ' VALUES ("batch1", "sku1", 100, null)'
    )
    session.commit()
    with unit_of_work.start(session_factory) as uow:
        batch = uow.batches.get(reference='batch1')
        line = model.OrderLine('ol1', 'sku1', 10)
        batch.allocate(line)
        uow.commit()

    [[olid]] = session.execute(
        'SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku',
        dict(orderid='ol1', sku='sku1')
    )
    [[batchid]] = session.execute(
        'SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id'
        ' WHERE orderline_id=:orderid',
        dict(orderid=olid)
    )
    assert batchid == 'batch1'

