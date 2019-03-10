from sqlalchemy import Table, MetaData, Column, Integer, String, Date
from sqlalchemy.orm import mapper

import model


metadata = MetaData()

order_lines = Table(
    'order_lines', metadata,
    Column('orderid', String(255), primary_key=True),
    Column('sku', String(255), primary_key=True),
    Column('qty', Integer),
)

batches = Table(
    'batches', metadata,
    Column('reference', String(255), primary_key=True),
    Column('sku', String(255), primary_key=True),
    Column('_purchased_qty', Integer),
    Column('eta', Date),
)


def start_mappers():
    mapper(model.OrderLine, order_lines)
    mapper(model.Batch, batches)
