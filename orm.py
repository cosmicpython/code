from sqlalchemy import Table, MetaData, Column, Integer, String
from sqlalchemy.orm import mapper

import model


metadata = MetaData()

order_lines = Table(
    'order_lines', metadata,
    Column('orderid', String(255), primary_key=True),
    Column('sku', String(255), primary_key=True),
    Column('qty', Integer),
)


def start_mappers():
    mapper(model.OrderLine, order_lines)
