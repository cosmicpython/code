from datetime import datetime
from flask import Flask, jsonify, request
from allocation.domain import commands
from allocation.service_layer import unit_of_work
from allocation.service_layer.handlers import InvalidSku
from allocation import bootstrap, views

app = Flask(__name__)
uow = unit_of_work.SqlAlchemyUnitOfWork()
bus = bootstrap.bootstrap(uow=uow)


@app.route("/add_batch", methods=["POST"])
async def add_batch():
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    cmd = commands.CreateBatch(
        request.json["ref"], request.json["sku"], request.json["qty"], eta
    )
    await bus.handle_command(cmd)
    return "OK", 201


@app.route("/allocate", methods=["POST"])
async def allocate_endpoint():
    try:
        cmd = commands.Allocate(
            request.json["orderid"], request.json["sku"], request.json["qty"]
        )
        await bus.handle_command(cmd)
    except InvalidSku as e:
        return {"message": str(e)}, 400

    return "OK", 202


@app.route("/allocations/<orderid>", methods=["GET"])
async def allocations_view_endpoint(orderid):
    result = await views.allocations(orderid, uow)
    if not result:
        return "not found", 404
    return jsonify(result), 200
