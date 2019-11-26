import json
import logging
from dataclasses import asdict
import redis

from allocation import config, events

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())


def get_subscription(name):
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(name)

    for m in pubsub.listen():
        yield m


def publish(channel, event: events.Event):
    logging.debug('publishing: channel=%s, event=%s', channel, event)
    r.publish(channel, json.dumps(asdict(event)))
