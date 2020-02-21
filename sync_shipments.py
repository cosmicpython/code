import logging
import uuid
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional
import requests
import requests.exceptions

from domain import Shipment, OrderLine
from notifications import notify_delay, notify_new_large_shipment

API_URL = 'https://example.org'


def create_shipment(quantities: Dict[str, int], incoterm):
    reference = uuid.uuid4().hex[:10]
    order_lines = [OrderLine(sku=sku, qty=qty) for sku, qty in quantities.items()]
    shipment = Shipment(reference=reference, lines=order_lines, eta=None, incoterm=incoterm)
    shipment.save()
    sync_to_api(shipment)


def get_updated_eta(shipment):
    external_shipment_id = get_shipment_id(shipment.reference)
    if external_shipment_id is None:
        logging.warning(
            'tried to get updated eta for shipment %s not yet sent to partners',
            shipment.reference
        )
        return

    [journey] = requests.get(f"{API_URL}/shipments/{external_shipment_id}/journeys").json()['items']
    latest_eta = journey['eta']
    if latest_eta == shipment.eta:
        return
    logging.info(
        'setting new shipment eta for %s: %s (was %s)',
        shipment.reference, latest_eta, shipment.eta
    )
    if shipment.eta is not None and latest_eta > shipment.eta:
        notify_delay(shipment_ref=shipment.reference, delay=latest_eta - shipment.eta)
    if shipment.eta is None and shipment.incoterm == 'FOB' and len(shipment.lines) > 10:
        notify_new_large_shipment(shipment_ref=shipment.reference, eta=latest_eta)

    shipment.eta = latest_eta
    shipment.save()



def sync_to_api(shipment):
    external_shipment_id = get_shipment_id(shipment.reference)
    if external_shipment_id is None:
        requests.post(f'{API_URL}/shipments/', json={
            'client_reference': shipment.reference,
            'arrival_date': shipment.eta,
            'products': [
                {'sku': ol.sku, 'quantity': ol.quantity}
                for ol in shipment.lines
            ]
        })

    else:
        requests.put(f'{API_URL}/shipments/{external_shipment_id}', json={
            'client_reference': shipment.reference,
            'arrival_date': shipment.eta,
            'products': [
                {'sku': ol.sku, 'quantity': ol.quantity}
                for ol in shipment.lines
            ]
        })


def get_shipment_id(our_reference) -> Optional[str]:
    try:
        their_shipments = requests.get(f"{API_URL}/shipments/").json()['items']
        return next(
            (s for s in their_shipments if s['client_reference'] == our_reference),
            None
        )

    except requests.exceptions.RequestException:
        logging.exception('Error retrieving shipment')
        raise
