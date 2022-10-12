import abc
from domain import model
from typing import Iterable, AsyncIterator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, batch: model.Batch) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, ref: str) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, batch: model.Batch) -> None:
        batch_id = await self._add_batch(batch)
        await self._add_allocations(batch_id, batch._allocations)

    async def _add_batch(self, batch: model.Batch) -> int:
        async with self._session as session:
            async with session.begin():
                result = await session.execute(
                    text(
                        """
                        INSERT INTO batches (ref, sku, _purchased_quantity, eta) 
                        VALUES ( :ref, :sku, :_purchased_quantity, :eta )
                        RETURNING id
                        """
                    ),
                    dict(
                        ref=batch.ref,
                        sku=batch.sku,
                        _purchased_quantity=batch._purchased_quantity,
                        eta=batch.eta,
                    ),
                )
        [[batch_id]] = result
        return int(batch_id)

    async def _add_allocations(
        self, batch_id: int, allocations: Iterable[model.OrderLine]
    ) -> None:
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

    async def get(self, ref: str) -> model.Batch:
        async with self._session as session:
            [row] = await session.execute(
                text(
                    """
                    SELECT id, ref, sku, _purchased_quantity, eta
                    FROM batches
                    WHERE ref = :ref
                    """
                ),
                dict(ref=ref),
            )
        return model.Batch(
            ref=row.ref,
            sku=row.sku,
            _purchased_quantity=row._purchased_quantity,
            eta=row.eta
            _allocations=self._get_order_lines(batch_id=row.id)
        )

    async def _get_order_lines(self, batch_id: int) -> AsyncIterator[model.OrderLine]:
        async with self._session as session:
            rows = await session.execute(
                text(
                    """
                    SELECT orderid, sky, qty
                    FROM allocations
                    JOIN order_lines ON allocations.orderline_id = order_lines.id
                    WHERE batch_id = :batch_id
                    """
                ),
                dict(batch_id=batch_id),
            )
            for row in rows:
                yield model.OrderLine(
                    orderid=row.orderid,
                    sku=row.sku,
                    qty=row.qty
                )


    """
    async def list(self) -> List[model.Batch]:
        return self.session.query(model.Batch).all()
    """
