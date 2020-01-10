# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
from typing import Protocol
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session


from allocation import config
from allocation.adapters import repository
from . import messagebus



class AbstractUnitOfWork(Protocol):
    products: repository.TrackingRepository

    def __enter__(self) -> AbstractUnitOfWork:
        ...

    def __exit__(self, *args):
        ...

    def commit(self):
        ...

    def rollback(self):
        ...



class AutoRollbackUoW:

    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow
        self.products = self._uow.products

    def __enter__(self):
        return self._uow.__enter__()

    def __exit__(self, *args):
        self._uow.rollback()
        return self._uow.__exit__(*args)

    def __getattr__(self, name):
        return getattr(self._uow, name)



class EventPublishingUoW:

    def __init__(self, uow: AutoRollbackUoW):
        self._uow = uow
        self.products = self._uow.products

    def commit(self):
        self._uow.commit()
        self.publish_events()

    def publish_events(self):
        for product in self.products.seen:
            while product.events:
                event = product.events.pop(0)
                messagebus.handle(event)


    def __enter__(self):
        return self._uow.__enter__()
    def __exit__(self, *args):
        return self._uow.__exit__(*args)

    def __getattr__(self, name):
        return getattr(self._uow, name)



DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(
    config.get_postgres_uri(),
    isolation_level="SERIALIZABLE",
))

class SqlAlchemyUnitOfWork:

    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()  # type: Session
        self.products = repository.TrackingRepository(
            repository.SqlAlchemyRepository(self.session)
        )
        return self

    def __exit__(self, *args):
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
