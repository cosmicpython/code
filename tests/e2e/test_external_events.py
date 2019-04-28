import json
import time
import uuid
import pytest
import requests
import redis

from allocation import config

def random_ref(prefix):
    return prefix + '-' + uuid.uuid4().hex[:10]

def post_to_add_batch(ref, sku, qty, eta):
    url = config.get_api_url()
    r = requests.post(
        f'{url}/add_batch',
        json={'ref': ref, 'sku': sku, 'qty': qty, 'eta': eta}
    )
    assert r.status_code == 201


def post_to_allocate(orderid, sku, qty, expected_batch):
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json={
        'orderid': orderid, 'sku': sku, 'qty': qty,
    })
    assert r.status_code == 201
    assert r.json()['batchref'] == expected_batch


def wait_for(fn):
    timeout = time.time() + 3
    while time.time() < timeout:
        r = fn()
        if r:
            return r
        time.sleep(0.1)
    pytest.fail('f{fn} never returned anything truthy')

def wait_for_assertion(fn):
    timeout = time.time() + 3
    while True:
        try:
            fn()
            return
        except AssertionError:
            if time.time() > timeout:
                raise
        time.sleep(0.1)


def subscribe_to_allocated_events(r):
    print('subscribing to allocated events')
    pubsub = r.pubsub()
    pubsub.subscribe('line_allocated')
    confirmation = wait_for(pubsub.get_message)
    assert confirmation['type'] == 'subscribe'
    return pubsub


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
@pytest.mark.usefixtures('restart_redis_pubsub')
def test_change_batch_quantity_leading_to_reallocation():
    orderid, sku = random_ref('o'), random_ref('s')
    batch1, batch2 = random_ref('b1'), random_ref('b2')
    post_to_add_batch(batch1, sku, 10, '2011-01-02')
    post_to_add_batch(batch2, sku, 10, '2011-01-03')
    post_to_allocate(orderid, sku, 10, expected_batch=batch1)

    r = redis.Redis(**config.get_redis_host_and_port())
    pubsub = subscribe_to_allocated_events(r)

    print('sending change batch quantity for', batch1)
    r.publish('change_batch_quantity', json.dumps({
        'batchref': batch1, 'sku': sku, 'qty': 5
    }))

    print('waiting for reallocation event')
    messages = []
    def check_messages():
        messages.append(wait_for(pubsub.get_message))
        print(messages)
        data = json.loads(messages[-1]['data'])
        assert data['orderid'] == orderid
        assert data['batchref'] == batch2

    wait_for_assertion(check_messages)

