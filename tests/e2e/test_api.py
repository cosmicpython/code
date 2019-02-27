import uuid
import pytest
import requests

import config

def random_ref(prefix):
    return prefix + '-' + uuid.uuid4().hex[:10]

@pytest.mark.usefixtures('restart_api')
def test_happy_path_returns_201_and_allocated_batch(add_stock):
    sku, othersku = random_ref('s1'), random_ref('s2')
    batch1, batch2, batch3 = random_ref('b1'), random_ref('b2'), random_ref('b3')
    add_stock([
        (batch1, sku, 100, '2011-01-02'),
        (batch2, sku, 100, '2011-01-01'),
        (batch3, othersku, 100, None),
    ])
    data = {
        'orderid': random_ref('o'),
        'sku': sku,
        'qty': 3,
    }
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 201
    assert r.json()['batchid'] == batch2


@pytest.mark.usefixtures('restart_api')
def test_unhappy_path_returns_400_and_error_message():
    sku, order = random_ref('s'), random_ref('o')
    data = {'orderid': order, 'sku': sku, 'qty': 20}
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 400
    assert r.json()['message'] == f'Invalid sku {sku}'

