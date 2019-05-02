import abc
from allocation.domain import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class DjangoRepository(AbstractRepository):
    def __init__(self):
        from djangoproject.alloc import models

        self.django_models = models

    def add(self, batch):
        self.django_models.Batch.from_domain(batch).save()

    def get(self, reference):
        return (
            self.django_models.Batch.objects.filter(reference=reference)
            .first()
            .to_domain()
        )
