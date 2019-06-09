from typing import Set
import abc
from allocation import model

class AbstractRepository(abc.ABC):

    def __init__(self):
        self.seen = set()  # type: Set[model.Product]

    def add(self, product):
        self._add(product)
        self.seen.add(product)

    def get(self, sku):
        p = self._get(sku)
        if p:
            self.seen.add(p)
        return p

    @abc.abstractmethod
    def _add(self, product):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, sku):
        raise NotImplementedError



class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, product):
        self.session.add(product)

    def _get(self, sku):
        return self.session.query(model.Product).filter_by(sku=sku).first()

