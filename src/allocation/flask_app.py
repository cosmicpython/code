from datetime import datetime
from flask import Flask, jsonify, request
from allocation import commands, exceptions, messagebus, orm, unit_of_work, views

app = Flask(__name__)
orm.start_mappers()


@app.route("/add_batch", methods=['POST'])
def add_batch():
    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    command = commands.CreateBatch(
        request.json['ref'], request.json['sku'], request.json['qty'], eta,
    )
    messagebus.handle_command(command, unit_of_work.SqlAlchemyUnitOfWork())
    return 'OK', 201


@app.route("/allocate", methods=['POST'])
def allocate_endpoint():
    try:
        command = commands.Allocate(
            request.json['orderid'], request.json['sku'], request.json['qty'],
        )
        uow = unit_of_work.SqlAlchemyUnitOfWork()
        batchref = messagebus.handle_command(command, uow)
    except exceptions.InvalidSku as e:
        return jsonify({'message': str(e)}), 400

    return 'OK', 202


@app.route("/allocations/<orderid>", methods=['GET'])
def allocations_view_endpoint(orderid):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    result = views.allocations(orderid, uow)
    if not result:
        return 'not found', 404
    return jsonify(result), 200
