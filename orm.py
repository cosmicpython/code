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


class _DummyOrderLine:
    pass


mapper(_DummyOrderLine, order_lines)
mapper(Order, order, properties={
    '__lines': relationship(_DummyOrderLine)
})


from sqlalchemy import event

# standard decorator style
@event.listens_for(Order, 'load')
def custom_load(target, context):
    breakpoint()
    target._lines = {l.sku: l.qty for l in target.__lines}
