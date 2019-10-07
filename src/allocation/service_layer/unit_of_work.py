# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc
from typing import Callable
from sqlalchemy.orm.session import Session
from allocation.adapters import repository
from . import messagebus


SessionFactory = Callable[[], Session]


class AbstractUnitOfWork(abc.ABC):
    bus: messagebus.MessageBus
    products: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()
        self.publish_events()

    def publish_events(self):
        for product in self.products.seen:
            while product.events:
                event = product.events.pop(0)
                self.bus.handle(event)

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError



class SqlAlchemyUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory: SessionFactory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.products = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
