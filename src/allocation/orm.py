from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date,
    ForeignKey
)
from sqlalchemy.orm import mapper, relationship

import model


metadata = MetaData()

order_lines = Table(
    'order_lines', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('orderid', String(255)),
    Column('sku', String(255)),
    Column('qty', Integer, nullable=False),
)

batches = Table(
    'batches', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('reference', String(255)),
    Column('sku', String(255)),
    Column('_purchased_quantity', Integer, nullable=False),
    Column('eta', Date, nullable=True),
)

allocations = Table(
    'allocations', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('orderline_id', ForeignKey('order_lines.id')),
    Column('batch_id', ForeignKey('batches.id')),
)


def start_mappers():
    lines_mapper = mapper(model.OrderLine, order_lines)
    mapper(model.Batch, batches, properties={
        '_allocations': relationship(
            lines_mapper,
            secondary=allocations,
            collection_class=set,
        )
    })
