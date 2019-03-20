from flask import Flask, jsonify, request

from allocation import unit_of_work
from allocation import model
from allocation import services
from allocation import orm

app = Flask(__name__)
orm.start_mappers()

@app.route("/allocate", methods=['POST'])
def allocate_endpoint():
    line = model.OrderLine(
        request.json['orderid'],
        request.json['sku'],
        request.json['qty'],
    )
    try:
        batchid = services.allocate(line, unit_of_work.start)
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'batchid': batchid}), 201
