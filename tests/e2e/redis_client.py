import json
import redis

from allocation import config
from .wait_for import wait_for

r = redis.Redis(**config.get_redis_host_and_port())


def subscribe_to(channel):
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    confirmation = wait_for(pubsub.get_message)
    assert confirmation['type'] == 'subscribe'
    return pubsub


def publish_message(channel, message):
    r.publish(channel, json.dumps(message))
