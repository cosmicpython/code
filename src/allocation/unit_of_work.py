from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import config
from allocation import repository

default_session_factory = sessionmaker(bind=create_engine(config.get_postgres_uri()))

@contextmanager
def start(session_factory=default_session_factory):
    session = session_factory()
    try:
        yield _UnitOfWork(session)
    finally:
        session.rollback()


class _UnitOfWork:
    def __init__(self, session):
        self.session = session
        self.batches = repository.BatchRepository(session)

    def commit(self):
        self.session.commit()
