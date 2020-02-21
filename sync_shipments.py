import logging
from dataclasses import dataclass
from datetime import date
from typing import List, Optional
import requests
import requests.exceptions

from notifications import notify_delay, notify_new_large_shipment

API_URL = 'https://example.org'

@dataclass
class OrderLine:
    sku: str
    qty: int


@dataclass
class Shipment:
    reference: str
    lines: List[OrderLine]
    eta: Optional[date]
    incoterm: str


def set_eta(shipment, eta):
    logging.info(
        'setting new shipment eta for %s: %s (was %s)',
        shipment.reference, eta, shipment.eta
    )
    if shipment.eta is not None and eta > shipment.eta:
        notify_delay(shipment_ref=shipment.reference, delay=eta - shipment.eta)
    if shipment.eta is None and shipment.incoterm == 'FOB' and len(shipment.lines) > 10:
        notify_new_large_shipment(shipment_ref=shipment.reference, eta=eta)

    shipment.eta = eta
    sync_to_api(shipment)



def sync_to_api(shipment):
    external_shipment_id = get_shipment_id(shipment.reference)
    if external_shipment_id is None:
        requests.post(f'{API_URL}/shipments/', json={
            'client_reference': shipment.reference,
            'arrival_date': shipment.eta.isoformat()[:10],
            'products': [
                {'sku': ol.sku, 'quantity': ol.quantity}
                for ol in shipment.lines
            ]
        })

    else:
        requests.put(f'{API_URL}/shipments/{external_shipment_id}', json={
            'client_reference': shipment.reference,
            'arrival_date': shipment.eta.isoformat()[:10],
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
