import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from orm import metadata


@pytest.fixture
def db():
    engine = create_engine('sqlite:///:memory:', echo=True)
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

