from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date,
    ForeignKey
)
from sqlalchemy.orm import mapper, relationship

from allocation import model


metadata = MetaData()

order_lines = Table(
    'order_lines', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sku', String(255)),
    Column('qty', Integer, nullable=False),
    Column('orderid', String(255)),
)

products = Table(
    'products', metadata,
    Column('sku', String(255), primary_key=True),
    Column('version_number', Integer, nullable=False, server_default='0'),
)

batches = Table(
    'batches', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('reference', String(255)),
    Column('sku', ForeignKey('products.sku')),
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
    batches_mapper = mapper(model.Batch, batches, properties={
        '_allocations': relationship(
            lines_mapper,
            secondary=allocations,
            collection_class=set,
        )
    })
    mapper(model.Product, products, properties={
        'batches': relationship(batches_mapper)
    })
