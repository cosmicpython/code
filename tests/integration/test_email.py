#pylint: disable=redefined-outer-name
import uuid
import pytest
import requests
from allocation import config, commands, messagebus, notifications, unit_of_work

email_config = config.get_email_host_and_port()

@pytest.fixture
def bus(sqlite_session_factory):
    return messagebus.MessageBus(
        uow=unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory),
        notifications=notifications.EmailNotifications(
            smtp_host=email_config['host'],
            port=email_config['port'],
        ),
        publish=lambda *_, **__: None
    )


def random_sku():
    return uuid.uuid4().hex[:6]


def test_out_of_stock_email(bus):
    sku = random_sku()
    bus.handle([
        commands.CreateBatch('batch1', sku, 9, None),
        commands.Allocate('order1', sku, 10),
    ])
    messages = requests.get(
        f'http://{email_config["host"]}:{email_config["http_port"]}/api/v2/messages'
    ).json()
    message = next(
        m for m in messages['items']
        if sku in str(m)
    )
    assert message['Raw']['From'] == 'allocations@example.com'
    assert message['Raw']['To'] == ['stock@made.com']
    assert f'Out of stock for {sku}' in message['Raw']['Data']
