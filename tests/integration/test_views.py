from datetime import date
from allocation import commands, events, unit_of_work, messagebus, views


def test_allocations_view(sqlite_session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory)
    messagebus.handle([
        commands.CreateBatch('b1', 'sku1', 50, None),
        commands.CreateBatch('b2', 'sku2', 50, date.today()),
        commands.Allocate('o1', 'sku1', 20),
        commands.Allocate('o1', 'sku2', 20),
    ], uow)

    assert views.allocations('o1', uow) == [
        {'sku': 'sku1', 'batchref': 'b1'},
        {'sku': 'sku2', 'batchref': 'b2'},
    ]


def test_deallocation(sqlite_session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory)
    messagebus.handle([
        commands.CreateBatch('b1', 'sku1', 50, None),
        commands.CreateBatch('b2', 'sku1', 50, date.today()),
        commands.Allocate('o1', 'sku1', 40),
        commands.ChangeBatchQuantity('b1', 10)
    ], uow)

    assert views.allocations('o1', uow) == [
        {'sku': 'sku1', 'batchref': 'b2'},
    ]


