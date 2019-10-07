import json
import logging
import redis

from allocation import config
from allocation.domain import commands
from allocation.adapters import email, orm, redis_eventpublisher
from allocation.service_layer import messagebus, unit_of_work

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())

def get_bus():
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    bus = messagebus.MessageBus(
        uow=uow,
        send_mail=email.send,
        publish=redis_eventpublisher.publish
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


if __name__ == '__main__':
    orm.start_mappers()
    main()
