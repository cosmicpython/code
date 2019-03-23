# pylint: disable=attribute-defined-outside-init
import abc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from allocation import config
from allocation import repository


class AbstractUnitOfWork(abc.ABC):

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

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

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

