import json
from dataclasses import asdict
import redis

from allocation import config, commands, events, orm, messagebus, unit_of_work

r = redis.Redis(**config.get_redis_host_and_port())


def main():
    orm.start_mappers()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('change_batch_quantity')

    for m in pubsub.listen():
        handle_change_batch_quantity(m)


def handle_change_batch_quantity(m):
    print('handling', m, flush=True)
    data = json.loads(m['data'])
    command = commands.ChangeBatchQuantity(ref=data['batchref'], qty=data['qty'])
    messagebus.handle_command(command, uow=unit_of_work.SqlAlchemyUnitOfWork())


def publish(channel, event: events.Event):
    print('publishing', channel, event, flush=True)
    r.publish(channel, json.dumps(asdict(event)))


if __name__ == '__main__':
    main()
