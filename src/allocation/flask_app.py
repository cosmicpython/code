from datetime import datetime
from flask import Flask, jsonify, request
from allocation import commands, exceptions, messagebus, orm, unit_of_work

app = Flask(__name__)
orm.start_mappers()


@app.route("/add_batch", methods=['POST'])
def add_batch():
    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    cmd = commands.CreateBatch(
        request.json['ref'], request.json['sku'], request.json['qty'], eta,
    )
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    messagebus.handle(cmd, uow)
    return 'OK', 201


@app.route("/allocate", methods=['POST'])
def allocate_endpoint():
    try:
        cmd = commands.Allocate(
            request.json['orderid'], request.json['sku'], request.json['qty'],
        )
        uow = unit_of_work.SqlAlchemyUnitOfWork()
        batchref = messagebus.handle(cmd, uow)
    except exceptions.InvalidSku as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'batchref': batchref}), 201
