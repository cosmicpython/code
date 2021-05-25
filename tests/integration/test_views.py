# pylint: disable=redefined-outer-name
from datetime import date
from sqlalchemy.orm import clear_mappers
from unittest import mock
import pytest
from allocation import bootstrap, views
from allocation.domain import commands
from allocation.service_layer import unit_of_work

today = date.today()


@pytest.fixture
def sqlite_bus(sqlite_session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory)
    bus = bootstrap.bootstrap(
        start_orm=True,
        uow=uow,
        notifications=mock.Mock(),
        publish=lambda *args: None,
    )
    yield bus, uow
    clear_mappers()


async def test_allocations_view(sqlite_bus):
    sqlite_bus, uow = sqlite_bus
    await sqlite_bus.handle_command(commands.CreateBatch("sku1batch", "sku1", 50, None))
    await sqlite_bus.handle_command(commands.CreateBatch("sku2batch", "sku2", 50, today))
    await sqlite_bus.handle_command(commands.Allocate("order1", "sku1", 20))
    await sqlite_bus.handle_command(commands.Allocate("order1", "sku2", 20))
    # add a spurious batch and order to make sure we're getting the right ones
    await sqlite_bus.handle_command(commands.CreateBatch("sku1batch-later", "sku1", 50, today))
    await sqlite_bus.handle_command(commands.Allocate("otherorder", "sku1", 30))
    await sqlite_bus.handle_command(commands.Allocate("otherorder", "sku2", 10))

    assert (await views.allocations("order1", uow)) == [
        {"sku": "sku1", "batchref": "sku1batch"},
        {"sku": "sku2", "batchref": "sku2batch"},
    ]


async def test_deallocation(sqlite_bus):
    sqlite_bus, uow = sqlite_bus
    await sqlite_bus.handle_command(commands.CreateBatch("b1", "sku1", 50, None))
    await sqlite_bus.handle_command(commands.CreateBatch("b2", "sku1", 50, today))
    await sqlite_bus.handle_command(commands.Allocate("o1", "sku1", 40))
    await sqlite_bus.handle_command(commands.ChangeBatchQuantity("b1", 10))

    assert views.allocations("o1", uow) == [
        {"sku": "sku1", "batchref": "b2"},
    ]
