# pylint: disable=too-many-arguments
import threading
import time
import traceback
import uuid
from typing import List

import pytest
from allocation import model, unit_of_work

def random_ref(prefix):
    return prefix + '-' + uuid.uuid4().hex[:10]

def insert_batch(session, ref, sku, qty, eta, product_version=1):
    session.execute(
        'INSERT INTO products (sku, version_number) VALUES (:sku, :version)',
        dict(sku=sku, version=product_version),
    )
    session.execute(
        'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
        ' VALUES (:ref, :sku, :qty, :eta)',
        dict(ref=ref, sku=sku, qty=qty, eta=eta)
    )

def get_allocated_batch_ref(session, orderid, sku):
    [[orderlineid]] = session.execute(
        'SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku',
        dict(orderid=orderid, sku=sku)
    )
    [[batchref]] = session.execute(
        'SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id'
        ' WHERE orderline_id=:orderlineid',
        dict(orderlineid=orderlineid)
    )
    return batchref


def test_uow_can_retrieve_a_batch_and_allocate_to_it(sqlite_session_factory):
    session = sqlite_session_factory()
    insert_batch(session, 'batch1', 'HIPSTER-WORKBENCH', 100, None)
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory)
    with uow:
        product = uow.products.get(sku='HIPSTER-WORKBENCH')
        line = model.OrderLine('o1', 'HIPSTER-WORKBENCH', 10)
        product.allocate(line)
        uow.commit()

    batchref = get_allocated_batch_ref(session, 'o1', 'HIPSTER-WORKBENCH')
    assert batchref == 'batch1'


def test_rolls_back_uncommitted_work_by_default(sqlite_session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory)
    with uow:
        insert_batch(uow.session, 'batch1', 'MEDIUM-PLINTH', 100, None)

    new_session = sqlite_session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []


def test_rolls_back_on_error(sqlite_session_factory):
    class MyException(Exception):
        pass

    uow = unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_batch(uow.session, 'batch1', 'LARGE-FORK', 100, None)
            raise MyException()

    new_session = sqlite_session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []


def try_to_allocate(orderid, sku, exceptions, session_factory):
    line = model.OrderLine(orderid, sku, 10)
    try:
        with unit_of_work.SqlAlchemyUnitOfWork(session_factory) as uow:
            product = uow.products.get(sku=sku)
            product.allocate(line)
            time.sleep(0.2)
            uow.commit()
    except Exception as e: # pylint: disable=broad-except
        print(traceback.format_exc())
        exceptions.append(e)


def test_concurrent_updates_to_version_are_not_allowed(postgres_session_factory):
    sku, batch = random_ref('s'), random_ref('b')
    session = postgres_session_factory()
    insert_batch(session, batch, sku, 100, eta=None, product_version=3)
    session.commit()

    exceptions = []  # type: List[Exception]
    o1, o2 = random_ref('o1'), random_ref('o2')
    target1 = lambda: try_to_allocate(o1, sku, exceptions, postgres_session_factory)
    target2 = lambda: try_to_allocate(o2, sku, exceptions, postgres_session_factory)
    t1 = threading.Thread(target=target1)
    t2 = threading.Thread(target=target2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    [[version]] = session.execute(
        "SELECT version_number FROM products WHERE sku=:sku",
        dict(sku=sku),
    )
    assert version == 4
    exception = [exceptions]
    assert 'could not serialize access due to concurrent update' in str(exception)

    orders = list(session.execute(
        "SELECT orderid FROM allocations"
        " JOIN batches ON allocations.batch_id = batches.id"
        " JOIN order_lines ON allocations.orderline_id = order_lines.id"
        " WHERE order_lines.sku=:sku",
        dict(sku=sku),
    ))
    assert len(orders) == 1
    with unit_of_work.SqlAlchemyUnitOfWork(postgres_session_factory) as uow:
        uow.session.execute('select 1')

