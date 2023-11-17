# pylint: disable=unused-argument
from __future__ import annotations
from dataclasses import asdict
from typing import List, Dict, Callable, Type, TYPE_CHECKING
from allocation.domain import commands, events, model
from allocation.domain.model import OrderLine
from sqlalchemy.sql import text

if TYPE_CHECKING:
    from allocation.adapters import notifications
    from . import unit_of_work


class InvalidSku(Exception):
    pass


def add_batch(
    cmd: commands.CreateBatch,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        product = uow.products.get(sku=cmd.sku)
        if product is None:
            product = model.Product(cmd.sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(cmd.ref, cmd.sku, cmd.qty, cmd.eta))
        uow.commit()


def allocate(
    cmd: commands.Allocate,
    uow: unit_of_work.AbstractUnitOfWork,
):
    line = OrderLine(cmd.orderid, cmd.sku, cmd.qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        product.allocate(line)
        uow.commit()


def reallocate(
    event: events.Deallocated,
    uow: unit_of_work.AbstractUnitOfWork,
):
    allocate(commands.Allocate(**asdict(event)), uow=uow)


def change_batch_quantity(
    cmd: commands.ChangeBatchQuantity,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        product = uow.products.get_by_batchref(batchref=cmd.ref)
        product.change_batch_quantity(ref=cmd.ref, qty=cmd.qty)
        uow.commit()


# pylint: disable=unused-argument


def send_out_of_stock_notification(
    event: events.OutOfStock,
    notifications: notifications.AbstractNotifications,
):
    notifications.send(
        "stock@made.com",
        f"Out of stock for {event.sku}",
    )


def publish_allocated_event(
    event: events.Allocated,
    publish: Callable,
):
    publish("line_allocated", event)


def add_allocation_to_read_model(
    event: events.Allocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            text(
                "INSERT INTO allocations_view (orderid, sku, batchref)"
                " VALUES (:orderid, :sku, :batchref)"
            ),
            dict(orderid=event.orderid, sku=event.sku, batchref=event.batchref),
        )
        uow.commit()


def remove_allocation_from_read_model(
    event: events.Deallocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            text(
                "DELETE FROM allocations_view"
                " WHERE orderid = :orderid AND sku = :sku"
            ),
            dict(orderid=event.orderid, sku=event.sku),
        )
        uow.commit()


EVENT_HANDLERS = {
    events.Allocated: [publish_allocated_event, add_allocation_to_read_model],
    events.Deallocated: [remove_allocation_from_read_model, reallocate],
    events.OutOfStock: [send_out_of_stock_notification],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.Allocate: allocate,
    commands.CreateBatch: add_batch,
    commands.ChangeBatchQuantity: change_batch_quantity,
}  # type: Dict[Type[commands.Command], Callable]
