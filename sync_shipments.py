import logging
from dataclasses import dataclass
from datetime import date
from typing import List
import requests
import requests.exceptions

API_URL = 'https://example.org'

@dataclass
class OrderLine:
    sku: str
    qty: int


@dataclass
class Shipment:
    reference: str
    lines: List[OrderLine]
    eta: date


def update_shipment(shipment):
    external_shipment_id = get_shipment_id(shipment.reference)
    requests.put(f'{API_URL}/shipment/{external_shipment_id}', json={
        'client_reference': shipment.reference,
        'arrival_date': shipment.eta,
        'contents': [
            {'sku': ol.sku, 'quantity': ol.quantity}
            for ol in shipment.lines
        ]
    })


def get_shipment_id(our_reference):
    try:
        their_shipments = requests.get(f"{API_URL}/shipment/").json()['items']
        return next(s for s in their_shipments if s['client_reference'] == our_reference)
    except StopIteration:
        logging.error('No shipment found with reference %s', our_reference)

    except requests.exceptions.RequestException:
        logging.exception('Error retrieving shipment')
