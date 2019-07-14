#pylint: disable=redefined-outer-name
import uuid
import pytest
import requests
from allocation import config, commands, messagebus, notifications, unit_of_work

cfg = config.get_email_host_and_port()

@pytest.fixture
def bus(sqlite_session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory)
    bus = messagebus.MessageBus(
        uow=uow,
        notifications=notifications.EmailNotifications(
            smtp_host=cfg['host'],
            port=cfg['port'],
        ),
        publish=lambda *_, **__: None
    )
    uow.bus = bus
    return bus


def random_sku():
    return uuid.uuid4().hex[:6]


def test_out_of_stock_email(bus):
    sku = random_sku()
    bus.handle(commands.CreateBatch('batch1', sku, 9, None))
    bus.handle(commands.Allocate('order1', sku, 10))
    messages = requests.get(
        f'http://{cfg["host"]}:{cfg["http_port"]}/api/v2/messages'
    ).json()
    message = next(
        m for m in messages['items']
        if sku in str(m)
    )
    assert message['Raw']['From'] == 'allocations@example.com'
    assert message['Raw']['To'] == ['stock@made.com']
    assert f'Out of stock for {sku}' in message['Raw']['Data']
