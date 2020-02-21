from __future__ import annotations
import logging
from datetime import date
from typing import Protocol, Optional
import requests
import requests.exceptions

from domain import Shipment


class CargoAPI(Protocol):

    def get_latest_eta(self, reference: str) -> date:
        ...

    def sync(self, shipment: Shipment) -> None:
        ...



class RealCargoAPI:
    API_URL = 'https://example.org'


    def get_latest_eta(self, reference: str) -> date:
        external_shipment_id = self._get_shipment_id(reference)
        if external_shipment_id is None:
            logging.warning(
                'tried to get updated eta for shipment %s not yet sent to partners',
                reference
            )
            return None

        [journey] = requests.get(f"{self.API_URL}/shipments/{external_shipment_id}/journeys").json()['items']
        return date.fromisoformat(journey['eta'])



    def sync(self, shipment: Shipment) -> None:
        external_shipment_id = self._get_shipment_id(shipment.reference)
        if external_shipment_id is None:
            requests.post(f'{self.API_URL}/shipments/', json={
                'client_reference': shipment.reference,
                'arrival_date': shipment.eta.isoformat()[:10] if shipment.eta else None,
                'products': [
                    {'sku': ol.sku, 'quantity': ol.qty}
                    for ol in shipment.lines
                ]
            })

        else:
            requests.put(f'{self.API_URL}/shipments/{external_shipment_id}/', json={
                'client_reference': shipment.reference,
                'arrival_date': shipment.eta.isoformat()[:10] if shipment.eta else None,
                'products': [
                    {'sku': ol.sku, 'quantity': ol.qty}
                    for ol in shipment.lines
                ]
            })


    def _get_shipment_id(self, our_reference) -> Optional[str]:
        try:
            their_shipments = requests.get(f"{self.API_URL}/shipments/").json()['items']
            return next(
                (s['id'] for s in their_shipments if s['client_reference'] == our_reference),
                None
            )

        except requests.exceptions.RequestException:
            logging.exception('Error retrieving shipment')
            raise
