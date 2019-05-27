from typing import Set
import abc
from allocation.domain import model


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[model.Batch]

    def add(self, batch: model.Batch):
        self.seen.add(batch)

    def get(self, reference) -> model.Batch:
        p = self._get(reference)
        if p:
            self.seen.add(p)
        return p

    @abc.abstractmethod
    def _get(self, sku):
        raise NotImplementedError


class DjangoRepository(AbstractRepository):
    def __init__(self):
        from djangoproject.alloc import models

        self.django_models = models

    def add(self, batch):
        self.django_models.Batch.update_from_domain(batch)

    def get(self, reference):
        return (
            self.django_models.Batch.objects.filter(reference=reference)
            .first()
            .to_domain()
        )
