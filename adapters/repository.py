import abc
from domain import model
from typing import Iterable


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self._session = session

    async def add(self, batch):
        batch_id = await self._add_batch(batch)
        await self._add_allocations(batch_id, batch._allocations)

    async def _add_batch(self, batch: model.Batch):
        async with self._session as session:
            async with session.begin():
                result = await session.execute(
                    """
                    INSERT INTO batches (ref, sku, _purchased_quantity, eta) 
                    VALUES ( :ref, :sku, :_purchased_quantity, :eta )
                    RETURNING id
                    """,
                    dict(ref=batch.ref, sku=batch.sku, _purchased_quantity=batch._purchased_quantity, eta=batch.eta),

                )
        [batch_id] = result
        return batch_id

    async def _add_allocations(self, batch_id: int, allocations: Iterable[model.OrderLine]):
        return
        # for line in allocations:
        #     async with self._session as session:
        #         await session.execute(
        #             """
        #             INSERT INTO order_lines (orderline_id, batch_id) 
        #             VALUES ( %{orderline_id}d, %{batch_id}d )
        #             ON CONFLICT DO UPDATE SET
        #                 orderline_id=%{orderline_id}d,
        #                 batchid=%{batch_id}d,
        #             """,
        #             dict(batch_id=batch_id, orderline_id=
        #         )

    def get(self, reference):
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(model.Batch).all()
