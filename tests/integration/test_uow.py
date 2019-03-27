import uuid
import pytest
from allocation import model
from allocation import unit_of_work

def random_ref(prefix):
    return prefix + '-' + uuid.uuid4().hex[:10]

def test_uow_can_retrieve_a_product_and_allocate_to_it(session_factory):
    session = session_factory()
    session.execute(
        "INSERT INTO products (sku) VALUES ('sku1')"
    )
    session.execute(
        'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
        " VALUES ('batch1', 'sku1', 100, null)"
    )
    session.commit()
    with unit_of_work.start(session_factory) as uow:
        product = uow.products.get(sku='sku1')
        line = model.OrderLine('ol1', 'sku1', 10)
        product.allocate(line)
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
            " VALUES ('batch1', 'sku1', 100, null)"
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


import threading
import traceback
import time

def try_to_allocate(sku, session_factory, exceptions):
    line = model.OrderLine(random_ref('o'), sku, 10)
    try:
        with unit_of_work.start(session_factory) as uow:
            product = uow.products.get(sku=sku)
            product.allocate(line)
            time.sleep(0.2)
            uow.commit()
    except Exception as e:
        print(traceback.format_exc())
        exceptions.append(e)


def test_concurrent_sessions_cannot_both_increment_product_version(postgres_session_factory):
    sku, batch = random_ref('s'), random_ref('b')
    session = postgres_session_factory()
    session.execute(
        "INSERT INTO products (sku, version_number) VALUES (:sku, 3)",
        dict(sku=sku),
    )
    session.execute(
        'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
        " VALUES (:batch, :sku, 100, null)",
        dict(batch=batch, sku=sku),
    )
    session.commit()
    exceptions = []
    target = lambda: try_to_allocate(sku, postgres_session_factory, exceptions)
    t1 = threading.Thread(target=target)
    t2 = threading.Thread(target=target)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    [[version]] = session.execute(
        "SELECT version_number FROM products WHERE sku=:sku",
        dict(sku=sku),
    )
    assert exceptions == []
    assert version == 4
    assert list(session.execute(
        "SELECT * FROM allocations JOIN batches on allocations.batch_id = batches.id WHERE sku=:sku",
        dict(sku=sku),
    )) == []

