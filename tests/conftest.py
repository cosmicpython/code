# pylint: disable=redefined-outer-name
import time
from pathlib import Path

import pytest
import pytest_asyncio
import requests
from requests.exceptions import ConnectionError
from typing import Callable
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
)

from sqlalchemy.orm import sessionmaker, clear_mappers

from adapters.orm import metadata
import config


@pytest_asyncio.fixture
async def in_memory_db() -> AsyncEngine:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    return engine

AsyncSessionMaker = Callable[[], AsyncSession]

@pytest_asyncio.fixture
async def session_maker(in_memory_db: AsyncEngine) -> AsyncSessionMaker:
    return sessionmaker(bind=in_memory_db, class_=AsyncSession)


"""
def wait_for_postgres_to_come_up(engine: AsyncEngine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return await engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("Postgres never came up")


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture(scope="session")
def postgres_db():
    engine = create_engine(config.get_postgres_uri())
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session(postgres_db):
    start_mappers()
    yield sessionmaker(bind=postgres_db)()
    clear_mappers()


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../entrypoints/flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
"""
