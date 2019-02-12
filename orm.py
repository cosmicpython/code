from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey
from sqlalchemy import event
from sqlalchemy.orm import mapper, relationship

from domain_model import Order


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

from dataclasses import dataclass

@dataclass
class _DummyOrderLine:
    '''dummy type to map order lines, will convert them to and from dicts in events below'''
    order_id: int
    sku: str
    qty: int


mapper(_DummyOrderLine, order_lines)
mapper(Order, order, properties={
    '__lines': relationship(_DummyOrderLine),
})



@event.listens_for(Order, 'load')
def custom_load(target, context):
    target._lines = {l.sku: l.qty for l in target.__lines}
    target.__lines.clear()

@event.listens_for(Order, 'after_insert')
def custom_insert(mapper, connection, target):
    for sku, qty in target._lines.items():
        target.__lines.append(_DummyOrderLine(order_id=target.id, sku=sku, qty=qty))

@event.listens_for(_DummyOrderLine, 'before_insert')
def custom_update(mapper, connection, target):
    breakpoint()
    print(target)
