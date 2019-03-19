import uuid
import pytest
import requests

import config

def random_ref(prefix):
    return prefix + '-' + uuid.uuid4().hex[:10]

@pytest.mark.usefixtures('restart_api')
def test_api_returns_allocation(add_stock):
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
def test_allocations_are_persisted(add_stock):
    sku = random_ref('s1')
    batch1, batch2 = random_ref('b1'), random_ref('b2')
    order1, order2 = random_ref('o1'), random_ref('o2')
    add_stock([
        (batch1, sku, 10, '2011-01-01'),
        (batch2, sku, 10, '2011-01-02'),
    ])
    line1 = {'orderid': order1, 'sku': sku, 'qty': 10}
    line2 = {'orderid': order2, 'sku': sku, 'qty': 10}
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=line1)
    assert r.status_code == 201
    assert r.json()['batchid'] == batch1
    r = requests.post(f'{url}/allocate', json=line2)
    assert r.status_code == 201
    assert r.json()['batchid'] == batch2

@pytest.mark.usefixtures('restart_api')
def test_400_message_for_out_of_stock(add_stock):
    sku, batch, order = random_ref('s'), random_ref('b'), random_ref('o')
    add_stock([
        (batch, sku, 10, '2011-01-01'),
    ])
    data = {'orderid': order, 'sku': sku, 'qty': 20}
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 400
    assert r.json()['message'] == f'Out of stock for sku {sku}'


@pytest.mark.usefixtures('restart_api')
def test_400_message_for_invalid_sku():
    sku, order = random_ref('s'), random_ref('o')
    data = {'orderid': order, 'sku': sku, 'qty': 20}
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 400
    assert r.json()['message'] == f'Invalid sku {sku}'

