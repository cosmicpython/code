from datetime import datetime
import time

import pytest
import requests
from requests import ConnectionError
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, clear_mappers

from orm import metadata, start_mappers
from config import DB_LINK, APP_URL


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()


def wait_for_postgress_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            engine.connect().execute(text('SELECT'))
            return
        except SQLAlchemyError:
            time.sleep(0.5)

    pytest.fail('BD was never up')


@pytest.fixture
def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            requests.get(APP_URL)
            return
        except ConnectionError:
            time.sleep(0.5)


@pytest.fixture(scope="session")
def postgress_db():
    engine = create_engine(DB_LINK)
    wait_for_postgress_to_come_up(engine)
    return engine


@pytest.fixture
def postgress_session(postgress_db):
    start_mappers()
    metadata.create_all(bind=postgress_db)
    yield sessionmaker(bind=postgress_db)
    clear_mappers()


@pytest.fixture
def add_stock(postgress_session):
    added_batches = set()
    added_skus = set()

    def _add_stock(batches):
        with postgress_session() as session:
            session.execute(text('DELETE FROM allocations'))
            session.execute(text('DELETE FROM batches'))
            session.execute(text('DELETE FROM order_lines'))
            session.commit()

        for ref, sku, qty, eta in batches:
            with postgress_session() as session:
                query = text(
                    'INSERT INTO batches (reference, sku, _purchased_quantity, eta) '
                    'VALUES (:ref, :sku, :qty, :eta)'
                )
                session.execute(query, dict(ref=ref, sku=sku, qty=qty, eta=eta))

                query = text('SELECT id FROM batches WHERE reference = :ref')
                [batch_id] = session.execute(query, dict(ref=ref)).one()

                added_batches.add(batch_id)
                added_skus.add(sku)
                session.commit()

    yield _add_stock

    with postgress_session() as session:
        for batch_id in added_batches:
            session.execute(text('DELETE FROM allocations WHERE batch_id = :batch_id'), dict(batch_id=batch_id))
            session.execute(text('DELETE FROM batches WHERE id = :batch_id'), dict(batch_id=batch_id))

        for sku in added_skus:
            session.execute(text('DELETE FROM order_lines WHERE sku = :sku'), dict(sku=sku))

        session.commit()