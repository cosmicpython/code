from typing import Dict
from collections import defaultdict
from unittest import mock
from allocation import messagebus, notifications, repository, unit_of_work


class FakeRepository(repository.AbstractRepository):

    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)

    def _get_by_batchref(self, batchref):
        return next((
            p for p in self._products for b in p.batches
            if b.reference == batchref
        ), None)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):

    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass



class FakeBus(messagebus.MessageBus):
    def __init__(self):
        uow = FakeUnitOfWork()
        super().__init__(
            uow=uow,
            notifications=FakeNotifications(),
            publish=mock.Mock(),
        )
        uow.bus = self


class FakeNotifications(notifications.AbstractNotifications):

    def __init__(self):
        self.sent = defaultdict(list)  # type: Dict[str, str]

    def send(self, destination, message):
        self.sent[destination].append(message)
