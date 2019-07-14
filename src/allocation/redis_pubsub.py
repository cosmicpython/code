import json
import logging
from dataclasses import asdict
import redis

from allocation import (
    config, commands, events, messagebus, notifications, orm, unit_of_work,
)

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())

def get_bus():
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    bus = messagebus.MessageBus(
        uow=uow,
        notifications=notifications.EmailNotifications(),
        publish=publish
    )
    uow.bus = bus
    return bus


def main():
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('change_batch_quantity')
    bus = get_bus()

    for m in pubsub.listen():
        handle_change_batch_quantity(m, bus)


def handle_change_batch_quantity(m, bus: messagebus.MessageBus):
    logging.debug('handling %s', m)
    data = json.loads(m['data'])
    cmd = commands.ChangeBatchQuantity(ref=data['batchref'], qty=data['qty'])
    bus.handle(cmd)


def publish(channel, event: events.Event):
    logging.debug('publishing: channel=%s, event=%s', channel, event)
    r.publish(channel, json.dumps(asdict(event)))


if __name__ == '__main__':
    orm.start_mappers()
    main()
