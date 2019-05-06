# pylint: disable=no-member, no-self-use
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
    def _get(self, reference):
        raise NotImplementedError


class DjangoRepository(AbstractRepository):
    def __init__(self):
        super().__init__()
        from djangoproject.alloc import models

        self.django_models = models

    def add(self, batch):
        super().add(batch)
        self.update(batch)

    def update(self, batch):
        self.django_models.Batch.update_from_domain(batch)

    def _get(self, reference):
        return (
            self.django_models.Batch.objects.filter(reference=reference)
            .first()
            .to_domain()
        )

    def list(self):
        return [b.to_domain() for b in self.django_models.Batch.objects.all()]
