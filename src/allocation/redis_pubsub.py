import json
import logging
from dataclasses import asdict
import redis

from allocation import config, events, orm, messagebus, unit_of_work

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())


def main():
    orm.start_mappers()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('change_batch_quantity')

    for m in pubsub.listen():
        handle_change_batch_quantity(m)


def handle_change_batch_quantity(m):
    logging.debug('handling %s', m)
    data = json.loads(m['data'])
    event = events.BatchQuantityChanged(ref=data['batchref'], qty=data['qty'])
    messagebus.handle([event], uow=unit_of_work.SqlAlchemyUnitOfWork())


def publish(channel, event):
    logging.debug('publishing: channel=%s, event=%s', channel, event)
    r.publish(channel, json.dumps(asdict(event)))


if __name__ == '__main__':
    main()
