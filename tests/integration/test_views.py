from datetime import date
import pytest
import redis
from allocation import config, views
from allocation.domain import commands
from allocation.service_layer import messagebus, unit_of_work

@pytest.fixture
def cleanup_redis():
    r = redis.Redis(**config.get_redis_host_and_port())
    yield
    for k in r.keys():
        print('cleaning up redis key', k)
        r.delete(k)

pytestmark = pytest.mark.usefixtures('cleanup_redis')


def test_allocations_view(sqlite_session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory)
    messagebus.handle(commands.CreateBatch('sku1batch', 'sku1', 50, None), uow)
    messagebus.handle(commands.CreateBatch('sku2batch', 'sku2', 50, date.today()), uow)
    messagebus.handle(commands.Allocate('order1', 'sku1', 20), uow)
    messagebus.handle(commands.Allocate('order1', 'sku2', 20), uow)
    # add a spurious batch and order to make sure we're getting the right ones
    messagebus.handle(commands.CreateBatch('sku1batch-later', 'sku1', 50, date.today()), uow)
    messagebus.handle(commands.Allocate('otherorder', 'sku1', 30), uow)
    messagebus.handle(commands.Allocate('otherorder', 'sku2', 10), uow)

    assert views.allocations('order1') == [
        {'sku': 'sku1', 'batchref': 'sku1batch'},
        {'sku': 'sku2', 'batchref': 'sku2batch'},
    ]


def test_deallocation(sqlite_session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory)
    messagebus.handle(commands.CreateBatch('b1', 'sku1', 50, None), uow)
    messagebus.handle(commands.CreateBatch('b2', 'sku1', 50, date.today()), uow)
    messagebus.handle(commands.Allocate('o1', 'sku1', 40), uow)
    messagebus.handle(commands.ChangeBatchQuantity('b1', 10), uow)

    assert views.allocations('o1') == [
        {'sku': 'sku1', 'batchref': 'b2'},
    ]
