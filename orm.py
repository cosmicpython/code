from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey
from sqlalchemy.orm import mapper, relationship, column_property
from sqlalchemy.orm.collections import attribute_mapped_collection, mapped_collection, collection

from domain_model import Order

metadata = MetaData()


order = Table(
    'order', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    # relationship('order_lines', secondary='order_lines')
)

order_lines = Table(
    'order_lines', metadata,
    Column('order_id', ForeignKey('order.id'), primary_key=True),
    Column('sku', String(255), primary_key=True),
    Column('qty', Integer),
)

mapper(Order, order)


from sqlalchemy import event

@event.listens_for(Order, 'load')
def custom_load(target, context):
    raw_lines = context.session.query(order_lines).join(order).filter_by(id=target.id).all()
    target._lines = {sku: qty for _, sku, qty in raw_lines}
