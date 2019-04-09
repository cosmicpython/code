import abc
from allocation import model

class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, product):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, sku):
        raise NotImplementedError



class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session):
        self.session = session
        self.seen = set()

    def add(self, product):
        self.seen.add(product)
        self.session.add(product)

    def get(self, sku):
        p = self.session.query(model.Product).filter_by(sku=sku).first()
        if p:
            self.seen.add(p)
        return p

