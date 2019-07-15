import json
from dataclasses import asdict
import redis

from allocation import (
    config, commands, email, events, messagebus, orm, unit_of_work,
)

r = redis.Redis(**config.get_redis_host_and_port())

def get_bus():
    return messagebus.MessageBus(
        uow=unit_of_work.SqlAlchemyUnitOfWork(),
        send_mail=email.send,
        publish=publish
    )


def main():
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('change_batch_quantity')
    bus = get_bus()

    for m in pubsub.listen():
        handle_change_batch_quantity(m, bus)


def handle_change_batch_quantity(m, bus: messagebus.MessageBus):
    print('handling', m, flush=True)
    data = json.loads(m['data'])
    command = commands.ChangeBatchQuantity(ref=data['batchref'], qty=data['qty'])
    bus.handle([command])


def publish(channel, event: events.Event):
    print('publishing', channel, event, flush=True)
    r.publish(channel, json.dumps(asdict(event)))


if __name__ == '__main__':
    orm.start_mappers()
    main()
