import subprocess
import time
import uuid
import pytest
import requests
from cargo_api import RealCargoAPI
from domain import Shipment, OrderLine

@pytest.fixture(autouse=True)
def restart_fake_webapp():
    subprocess.run('docker-compose exec -T fake_cargo_api touch /fake_cargo_api.py'.split())
    time.sleep(0.5)

def random_reference():
    return uuid.uuid4().hex[:6]


def test_can_create_new_shipment():
    api = RealCargoAPI('http://localhost:8543')
    line = OrderLine('sku1', 10)
    ref = random_reference()
    shipment = Shipment(reference=ref, lines=[line], eta=None, incoterm='foo')

    api.sync(shipment)

    shipments = requests.get(api.api_url + '/shipments/').json()['items']
    new_shipment = next(s for s in shipments if s['client_reference'] == ref)
    assert new_shipment['arrival_date'] is None
    assert new_shipment['products'] == [{'sku': 'sku1', 'quantity': 10}]


def test_can_update_a_shipment():
    api = RealCargoAPI('http://localhost:8543')
    line = OrderLine('sku1', 10)
    ref = random_reference()
    shipment = Shipment(reference=ref, lines=[line], eta=None, incoterm='foo')

    api.sync(shipment)

    shipment.lines[0].qty = 20

    api.sync(shipment)

    shipments = requests.get(api.api_url + '/shipments/').json()['items']
    new_shipment = next(s for s in shipments if s['client_reference'] == ref)
    assert new_shipment['products'] == [{'sku': 'sku1', 'quantity': 20}]

