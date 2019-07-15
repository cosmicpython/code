# pylint: disable=redefined-outer-name
import shutil
import subprocess
import time
from pathlib import Path

import pytest
import redis
from redis.exceptions import RedisError
import requests
from requests.exceptions import RequestException
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, clear_mappers

from allocation.orm import metadata, start_mappers
from allocation import config


@pytest.fixture
def in_memory_sqlite_db():
    engine = create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    return engine

@pytest.fixture
def sqlite_session_factory(in_memory_sqlite_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_sqlite_db)
    clear_mappers()


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail('Postgres never came up')


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except RequestException:
            time.sleep(0.5)
    pytest.fail('API never came up')


def wait_for_redis_to_come_up():
    deadline = time.time() + 5
    r = redis.Redis(**config.get_redis_host_and_port())
    while time.time() < deadline:
        try:
            return r.ping()
        except RedisError:
            time.sleep(0.5)
    pytest.fail('Redis never came up')


@pytest.fixture(scope='session')
def postgres_db():
    engine = create_engine(config.get_postgres_uri(), isolation_level='SERIALIZABLE')
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine

@pytest.fixture
def postgres_session_factory(postgres_db):
    start_mappers()
    yield sessionmaker(bind=postgres_db)
    clear_mappers()

@pytest.fixture
def postgres_session(postgres_session_factory):
    return postgres_session_factory()


@pytest.fixture
def restart_api():
    (Path(__file__).parent / '../src/allocation/flask_app.py').touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()

@pytest.fixture
def restart_redis_pubsub():
    wait_for_redis_to_come_up()
    if not shutil.which('docker-compose'):
        print('skipping restart, assumes running in container')
        return
    subprocess.run(['docker-compose', 'restart', '-t', '0', 'redis_pubsub'])

