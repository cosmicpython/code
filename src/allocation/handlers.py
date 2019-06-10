from __future__ import annotations
from typing import TYPE_CHECKING
from allocation import commands, events, email, exceptions, model, redis_pubsub
from allocation.model import OrderLine

if TYPE_CHECKING:
    from allocation import unit_of_work


def add_batch(
        event: commands.CreateBatch, uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        product = uow.products.get(sku=event.sku)
        if product is None:
            product = model.Product(event.sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(
            event.ref, event.sku, event.qty, event.eta
        ))
        uow.commit()


def allocate(
        event: commands.Allocate, uow: unit_of_work.AbstractUnitOfWork
):
    line = OrderLine(event.orderid, event.sku, event.qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise exceptions.InvalidSku(f'Invalid sku {line.sku}')
        product.allocate(line)
        uow.commit()


def change_batch_quantity(
        event: commands.ChangeBatchQuantity, uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        product = uow.products.get_by_batchref(batchref=event.ref)
        product.change_batch_quantity(ref=event.ref, qty=event.qty)
        uow.commit()


def send_out_of_stock_notification(
        event: events.OutOfStock, uow: unit_of_work.AbstractUnitOfWork,
):
    email.send(
        'stock@made.com',
        f'Out of stock for {event.sku}',
    )


def publish_allocated_event(
        event: events.Allocated, uow: unit_of_work.AbstractUnitOfWork,
):
    redis_pubsub.publish('line_allocated', event)
