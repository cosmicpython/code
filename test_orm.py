import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from orm import metadata
from domain_model import Order


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

def test_order_mapper_with_lines(session):
    session.execute('INSERT INTO "order" VALUES (1)')
    session.execute('INSERT INTO "order" VALUES (2)')
    session.execute('INSERT INTO "order_lines" VALUES (1, "sku1", 12)')
    session.execute('INSERT INTO "order_lines" VALUES (1, "sku2", 13)')
    session.execute('INSERT INTO "order_lines" VALUES (2, "sku3", 14)')
    expected_order = Order({'sku1': 12, 'sku2': 13})
    retrieved_order = session.query(Order).first()
    assert retrieved_order.lines == expected_order.lines
