import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from orm import metadata
from domain_model import Order, Warehouse


@pytest.fixture
def db():
    # engine = create_engine('sqlite:///:memory:', echo=True)
    engine = create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    return engine

@pytest.fixture
def session(db):
    return sessionmaker(bind=db)()

def test_smoke(session):
    session.execute('INSERT INTO "order" VALUES (1)')
    session.execute('INSERT INTO "order_lines" VALUES (1, "sku1", 12)')
    session.execute('INSERT INTO "order_lines" VALUES (1, "sku2", 13)')
    r = session.execute('SELECT * from "order" JOIN "order_lines"')
    assert list(r) == [
        (1, 1, "sku1", 12),
        (1, 1, "sku2", 13),
    ]

def test_order_mapper_no_lines(session):
    order = Order({})
    session.add(order)
    assert session.query(Order).first() == order

def test_order_mapper_can_load_lines(session):
    session.execute('INSERT INTO "order" VALUES (1)')
    session.execute('INSERT INTO "order" VALUES (2)')
    session.execute('INSERT INTO "order_lines" VALUES (1, "sku1", 12)')
    session.execute('INSERT INTO "order_lines" VALUES (1, "sku2", 13)')
    session.execute('INSERT INTO "order_lines" VALUES (2, "sku3", 14)')
    expected_order = Order({'sku1': 12, 'sku2': 13})
    retrieved_order = session.query(Order).first()
    assert retrieved_order.lines == expected_order.lines


def test_order_mapper_can_save_lines(session):
    new_order = Order({'sku1': 12, 'sku2': 13})
    session.add(new_order)
    session.commit()

    rows = list(session.execute('SELECT * FROM "order_lines"'))
    assert rows == [
        (1, 'sku1', 12),
        (1, 'sku2', 13),
    ]

def test_order_mapper_can_edit_lines(session):
    session.execute('INSERT INTO "order" VALUES (1)')
    session.execute('INSERT INTO "order" VALUES (2)')
    session.execute('INSERT INTO "order_lines" VALUES (1, "sku1", 12)')
    session.execute('INSERT INTO "order_lines" VALUES (1, "sku2", 13)')
    session.execute('INSERT INTO "order_lines" VALUES (2, "sku3", 14)')

    order = session.query(Order).first()
    order['sku4'] = 99
    session.add(order)
    session.commit()

    rows = list(session.execute('SELECT * FROM "order_lines" WHERE order_id=1'))
    assert rows == [
        (1, 'sku1', 12),
        (1, 'sku2', 13),
        (1, 'sku4', 99),
    ]


def test_order_mapper_can_delete_lines(session):
    session.execute('INSERT INTO "order" VALUES (1)')
    session.execute('INSERT INTO "order" VALUES (2)')
    session.execute('INSERT INTO "order_lines" VALUES (1, "sku1", 12)')
    session.execute('INSERT INTO "order_lines" VALUES (1, "sku2", 13)')
    session.execute('INSERT INTO "order_lines" VALUES (2, "sku3", 14)')

    order = session.query(Order).first()
    order.lines.remove(order.lines[0])
    session.add(order)
    session.commit()

    rows = list(session.execute('SELECT * FROM "order_lines" WHERE order_id=1'))
    assert rows == [
        (1, 'sku2', 13),
    ]




def test_rest_of_fields(session):
    new_order = Order({'sku1': 12, 'sku2': 13})
    warehouse = Warehouse({'whsku1': 11, 'whsku2': 12})
    session.add(new_order)
    session.add(warehouse)
    session.commit()

    warehouse_rows = list(session.execute('SELECT * FROM "warehouse_lines"'))
    assert warehouse_rows == [
        (1, 'whsku1', 12),
        (1, 'whsku2', 12),
    ]

    warehouse_rows = list(session.execute('SELECT * FROM "warehouse"'))
    assert warehouse_rows == [
        (1, 'whsku1', 12),
        (1, 'whsku2', 12),
    ]
