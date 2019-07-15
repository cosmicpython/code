# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from allocation import config, repository



class AbstractUnitOfWork(abc.ABC):

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()


    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    def collect_events(self):
        for product in self.products.seen:
            while product.events:
                yield product.events.pop(0)

    def init_repositories(self, products: repository.AbstractRepository):
        self._products = products

    @property
    def products(self) -> repository.AbstractRepository:
        return self._products



DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(
    config.get_postgres_uri(),
    isolation_level="SERIALIZABLE",
))

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session = session_factory()  # type: Session
        self.init_repositories(repository.SqlAlchemyRepository(self.session))

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
