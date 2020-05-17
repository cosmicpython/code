import logging
from datetime import datetime
import sqlalchemy
from flask import Flask, jsonify, request
from allocation.domain import commands
from allocation.service_layer.handlers import InvalidSku
from allocation.service_layer.unit_of_work import SqlAlchemyUnitOfWork
from allocation import bootstrap, views

logging.basicConfig()
logger = logging.getLogger(__name__)

app = Flask(__name__)
bus = bootstrap.bootstrap()



@app.route("/add_batch", methods=['POST'])
def add_batch():
    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    cmd = commands.CreateBatch(
        request.json['ref'], request.json['sku'], request.json['qty'], eta,
    )
    bus.handle(cmd)
    return 'OK', 201


@app.route("/allocate", methods=['POST'])
def allocate_endpoint():
    while True:
        try:
            cmd = commands.Allocate(
                request.json['orderid'], request.json['sku'], request.json['qty'],
            )
            uow = SqlAlchemyUnitOfWork()
            bus.handle(cmd)
            return 'OK', 202
        except InvalidSku as e:
            return jsonify({'message': str(e)}), 400
        except sqlalchemy.exc.OperationalError:
            logger.error("Could not allocate!!!!!!!!!!!!")
            # Just try again!



@app.route("/allocations/<orderid>", methods=['GET'])
def allocations_view_endpoint(orderid):
    uow = SqlAlchemyUnitOfWork()
    result = views.allocations(orderid, uow)
    if not result:
        return 'not found', 404
    return jsonify(result), 200
