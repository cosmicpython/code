import json

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from orm import start_mappers, metadata
from repository import SqlAlchemyRepository
from model import OrderLine
from services import allocate, InvalidSku
from config import DB_LINK

# docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -p 5555:5432 -d postgres
# flask --app flask_app run --debug
start_mappers()
engine = create_engine(DB_LINK)
metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

app = Flask(__name__)


@app.route('/allocate', methods=['POST'])
def allocate_endpoint():
    with Session() as session:
        rep = SqlAlchemyRepository(session)
        order_line = OrderLine(
            request.json['orderid'],
            request.json['sku'],
            request.json['qty']
        )
        try:
            batchref = allocate(order_line, rep, session)
            return json.dumps(batchref), 201
        except InvalidSku as e:
            return json.dumps(str(e)), 404
