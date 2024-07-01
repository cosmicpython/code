from datetime import datetime, timedelta

#from pytest.mark import usefixtures
import requests
from config import APP_URL
from conftest import add_stock


def test_requests(wait_for_webapp_to_come_up, add_stock):
    batches = [
        ('batch1', 'SKU1', 10, datetime.now() + timedelta(days=1)),
        ('batch2', 'SKU1', 10, datetime.now()),
        ('batch3', 'SKU2', 10, datetime.now()),
    ]
    add_stock(batches)
    data = {'orderid': 'orderid_1', 'sku': 'SKU1', 'qty': 10}
    response = requests.post(f'{APP_URL}/allocate', json=data)
    assert response.json() == 'batch2'
