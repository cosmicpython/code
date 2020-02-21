from unittest import mock

from use_cases import create_shipment, API_URL
from domain import Shipment, OrderLine
from cargo_api import RealCargoAPI

def test_create_shipment_syncs_to_api():
    with mock.patch('use_cases.cargo_api') as mock_cargo_api:
        shipment = create_shipment({'sku1': 10}, incoterm='EXW')
        assert mock_cargo_api.sync.call_args == mock.call(shipment)
