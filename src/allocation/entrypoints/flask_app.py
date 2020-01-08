from datetime import datetime
from flask import Flask, jsonify, request, redirect

from allocation.domain import commands
from allocation.adapters import notifications, orm, redis_eventpublisher
from allocation.service_layer import messagebus, unit_of_work
from allocation.service_layer.handlers import InvalidSku
from allocation import views

app = Flask(__name__)
orm.start_mappers()
uow = unit_of_work.SqlAlchemyUnitOfWork()
bus = messagebus.MessageBus(
    uow=uow,
    notifications=notifications.EmailNotifications(),
    publish=redis_eventpublisher.publish
)
uow.bus = bus



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
    try:
        orderid = request.json['orderid']
        cmd = commands.Allocate(
            orderid, request.json['sku'], request.json['qty'],
        )
        bus.handle(cmd)
        return redirect(f'/allocations/{orderid}', code=302)
    except InvalidSku as e:
        return jsonify({'message': str(e)}), 400



@app.route("/allocations/<orderid>", methods=['GET'])
def allocations_view_endpoint(orderid):
    result = views.allocations(orderid, bus.uow)
    if not result:
        return 'not found', 404
    return jsonify(result), 200
