import pytest
from allocation import model
from allocation import unit_of_work

def test_uow_can_retrieve_a_product_and_allocate_to_it(session_factory):
    session = session_factory()
    session.execute(
        'INSERT INTO products (sku) VALUES ("sku1")'
    )
    session.execute(
        'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
        ' VALUES ("batch1", "sku1", 100, null)'
    )
    session.commit()
    with unit_of_work.start(session_factory) as uow:
        batch = uow.products.get(sku='sku1')
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


def test_rolls_back_uncommitted_work_by_default(session_factory):
    with unit_of_work.start(session_factory) as uow:
        uow.session.execute(
            'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
            ' VALUES ("batch1", "sku1", 100, null)'
        )

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    with pytest.raises(MyException):
        with unit_of_work.start(session_factory) as uow:
            uow.session.execute(
                'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
                ' VALUES ("batch1", "sku1", 100, null)'
            )
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []
