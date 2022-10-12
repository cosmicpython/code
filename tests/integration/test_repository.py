# pylint: disable=protected-access
import pytest
from domain import model
from adapters import repository
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

AsyncSessionMaker = Callable[[], AsyncSession]


@pytest.mark.asyncio
async def test_repository_can_save_a_batch(session_maker: AsyncSessionMaker) -> None:
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    async with session_maker() as session:
        repo = repository.SqlAlchemyRepository(session)
        await repo.add(batch)

    async with session_maker() as session:
        async with session.begin():
            rows = await session.execute(
                text('SELECT ref, sku, _purchased_quantity, eta FROM "batches"')
            )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]


async def insert_order_line(session: AsyncSession) -> int:
    await session.execute(
        text(
            "INSERT INTO order_lines (orderid, sku, qty)"
            ' VALUES ("order1", "GENERIC-SOFA", 12)'
        )
    )
    [[orderline_id]] = await session.execute(
        text("SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid="order1", sku="GENERIC-SOFA"),
    )
    return int(orderline_id)


async def insert_batch(session: AsyncSession, batch_ref: str) -> int:
    await session.execute(
        text(
            "INSERT INTO batches (ref, sku, _purchased_quantity, eta)"
            ' VALUES (:batch_ref, "GENERIC-SOFA", 100, null)'
        ),
        dict(batch_ref=batch_ref),
    )
    [[batch_id]] = await session.execute(
        text(
            'SELECT id FROM batches WHERE ref=:batch_ref AND sku="GENERIC-SOFA"'
        ),
        dict(batch_ref=batch_ref),
    )
    return int(batch_id)


async def insert_allocation(
    session: AsyncSession, orderline_id: int, batch_id: int
) -> None:
    await session.execute(
        text(
            "INSERT INTO allocations (orderline_id, batch_id)"
            " VALUES (:orderline_id, :batch_id)",
        ),
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


@pytest.mark.asyncio
async def test_repository_can_retrieve_a_batch_with_allocations(
    session_maker: AsyncSessionMaker,
) -> None:
    async with session_maker() as session:
        async with session.begin():
            orderline_id = await insert_order_line(session)
            batch1_id = await insert_batch(session, "batch1")
            await insert_batch(session, "batch2")
            await insert_allocation(session, orderline_id, batch1_id)

    async with session_maker() as session:
        rows = await session.execute("SELECT * from batches")
        print(list(rows))

    async with session_maker() as session:
        repo = repository.SqlAlchemyRepository(session)
        retrieved = await repo.get("batch1")

    expected = model.Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected  # Batch.__eq__ only compares ref
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {
        model.OrderLine("order1", "GENERIC-SOFA", 12),
    }
