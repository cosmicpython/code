from datetime import date
from unittest import mock

from use_cases import create_shipment, API_URL
from domain import Shipment, OrderLine
from cargo_api import RealCargoAPI

class FakeCargoAPI:

    def __init__(self):
        self._shipments = {}

    def get_latest_eta(self, reference) -> date:
        return self._shipments[reference].eta

    def sync(self, shipment: Shipment):
        self._shipments[shipment.reference] = shipment

    def __contains__(self, shipment):
        return shipment in self._shipments.values()


def test_create_shipment_syncs_to_api():
    api = FakeCargoAPI()
    shipment = create_shipment({'sku1': 10}, incoterm='EXW', cargo_api=api)
    assert shipment in api
