import requests
from allocation import config


def post_to_add_batch(ref, sku, qty, eta):
    url = config.get_api_url()
    r = requests.post(
        f'{url}/add_batch',
        json={'ref': ref, 'sku': sku, 'qty': qty, 'eta': eta}
    )
    assert r.status_code == 201


def post_to_allocate(orderid, sku, qty, expect_success=True):
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json={
        'orderid': orderid, 'sku': sku, 'qty': qty,
    })
    # NOTE: print(r.history) will show the intermediate re-direct
    if expect_success:
        assert r.status_code == 200
    return r

def get_allocation(orderid):
    url = config.get_api_url()
    return requests.get(f'{url}/allocations/{orderid}')
