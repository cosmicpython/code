import abc
from typing import Set
from allocation import model


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, product: model.Product):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, sku) -> model.Product:
        raise NotImplementedError



class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session):
        self.session = session
        self.seen = set()  # type: Set[model.Product]

    def add(self, product):
        self.seen.add(product)
        self.session.add(product)

    def get(self, sku):
        product = self.session.query(model.Product).filter_by(sku=sku).first()
        if product:
            self.seen.add(product)
        return product
