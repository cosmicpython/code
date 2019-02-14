from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import mapper, relationship

import domain_model

# minimal mappings, just order and warehouse + their lines

metadata = MetaData()

order = Table(
    'order', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
)
order_lines = Table(
    'order_lines', metadata,
    Column('order_id', ForeignKey('order.id'), primary_key=True),
    Column('sku', String(255), primary_key=True),
    Column('qty', Integer),
)
mapper(domain_model.Line, order_lines)
mapper(domain_model.Order, order, properties={
    'lines': relationship(domain_model.Line, cascade="all, delete-orphan")
})


warehouse = Table(
    'warehouse', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
)
warehouse_lines = Table(
    'warehouse_lines', metadata,
    Column('warehouse_id', ForeignKey('warehouse.id'), primary_key=True),
    Column('sku', String(255), primary_key=True),
    Column('qty', Integer),
)
warehouse_line_mapper = mapper(domain_model.Line, warehouse_lines, non_primary=True)
mapper(domain_model.Warehouse, warehouse, properties={
    'lines': relationship(warehouse_line_mapper, cascade="all, delete-orphan")
})


