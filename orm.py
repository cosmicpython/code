from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import mapper, relationship

import domain_model


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


shipment = Table(
    'shipment', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('eta', Date),
)
shipment_lines = Table(
    'shipment_lines', metadata,
    Column('shipment_id', ForeignKey('shipment.id'), primary_key=True),
    Column('sku', String(255), primary_key=True),
    Column('qty', Integer),
)

shipment_line_mapper = mapper(domain_model.Line, shipment_lines, non_primary=True)
mapper(domain_model.Shipment, shipment, properties={
    'lines': relationship(shipment_line_mapper, cascade="all, delete-orphan")
})

allocation = Table(
    'allocation', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('order_id', ForeignKey('order.id'))
)

allocation_lines = Table(
    'allocation_lines', metadata,
    Column('allocation_id', ForeignKey('allocation.id'), primary_key=True),
    Column('sku', String(255), primary_key=True),
    Column('shipment_id', ForeignKey('shipment.id'), nullable=True),
)

mapper(domain_model.AllocationLine, allocation_lines)
mapper(domain_model.Allocation, allocation, properties={
    'lines': relationship(domain_model.AllocationLine, cascade="all, delete-orphan"),
})
