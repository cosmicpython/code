from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey
from sqlalchemy.orm import mapper, relationship

from domain_model import Order, Line


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


mapper(Line, order_lines)
mapper(Order, order, properties={
    'lines': relationship(Line, cascade="all, delete-orphan")
})

