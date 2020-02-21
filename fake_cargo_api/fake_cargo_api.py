import uuid
from typing import Dict
from flask import Flask, request

app = Flask('fake-cargo-api')

SHIPMENTS = {}  # type: Dict[str, Dict]

@app.route('/shipments/', methods=["GET"])
def list_shipments():
    print('returning', SHIPMENTS)
    return {'items': list(SHIPMENTS.values())}


@app.route('/shipments/', methods=["POST"])
def create_shipment():
    new_id = uuid.uuid4().hex
    refs = {s['client_reference'] for s in SHIPMENTS.values()}
    if request.json['client_reference'] in refs:
        return 'already exists', 400
    SHIPMENTS[new_id] = {'id': new_id, **request.json}
    print('saved', SHIPMENTS)
    return 'ok', 201


@app.route('/shipments/<shipment_id>/', methods=["PUT"])
def update_shipment(shipment_id):
    existing = SHIPMENTS[shipment_id]
    SHIPMENTS[shipment_id] = {**existing, **request.json}
    print('updated', SHIPMENTS)
    return 'ok', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8543, debug=True)
