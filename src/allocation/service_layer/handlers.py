#pylint: disable=unused-argument
from __future__ import annotations
from dataclasses import asdict
from typing import List, Dict, Callable, Type, TYPE_CHECKING
from allocation.domain import commands, events, model
from allocation.domain.model import OrderLine
from allocation.service_layer.unit_of_work import SqlAlchemyUnitOfWork

import logging
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from allocation.adapters import notifications
    from . import unit_of_work

def _noop(*args, **kwargs):
    # do nothing!
    pass

class Actor:
    def __init__(self, message):
        self.message = message
        self.uow = SqlAlchemyUnitOfWork()
        self.things_that_happened = []

    @classmethod
    def handle_message(cls, message):
        # NOTE: Preferable to move the uow scope here!
        actor = cls(message)
        actor.run_to_completion()
        return actor.things_that_happened

    def run_to_completion(self):
        messages = [self.message]
        while messages:
            message = messages.pop(0)
            if isinstance(message, events.Event):
                pending = list(self._dispatch_event(message))
                messages.extend(pending)
                self.things_that_happened.extend(pending)
            elif isinstance(message, commands.Command):
                pending = list(self._dispatch_command(message))
                messages.extend(pending)
                self.things_that_happened.extend(pending)
            else:
                raise Exception(f'{message} was not an Event or Command')

    def _dispatch_command(self, message):
        raise NotImplementedError()

    def _dispatch_event(self, message):
        raise NotImplementedError()

class ProductActor(Actor):
    @classmethod
    def register_with(cls, bus):
        bus.register_handler(cls.handle_message, commands.ChangeBatchQuantity)
        bus.register_handler(cls.handle_message, commands.Allocate)
        bus.register_handler(cls.handle_message, commands.CreateBatch)
        bus.register_handler(cls.handle_message, events.Deallocated)

    def _dispatch_command(self, command: commands.Command):
        logger.debug('handling command %s', command)

        if isinstance(command, commands.ChangeBatchQuantity):
            change_batch_quantity(command, self.uow)
        elif isinstance(command, commands.Allocate):
            allocate(command, self.uow)
        elif isinstance(command, commands.CreateBatch):
            add_batch(command, self.uow)
        else:
            raise Exception("Product doesn't know what to do with %s" % command)
        return self.uow.collect_new_events()

    def _dispatch_event(self, event: events.Event):
        if isinstance(event, events.Deallocated):
            reallocate(event, self.uow)
        else:
            logger.debug("Product doesn't know what to do with %s" % event)
        return self.uow.collect_new_events()

class TheExternalWorld(Actor): # Basically "the external message bus"
    external_publisher = _noop
    notifications = _noop

    @classmethod
    def register_with(cls, bus):
        bus.register_handler(cls.handle_message, events.Deallocated)
        bus.register_handler(cls.handle_message, events.Allocated)
        bus.register_handler(cls.handle_message, events.OutOfStock)

    def _dispatch_command(self, command: commands.Command):
        # TODO: Implement me! Not going to do bother because there
        # isn't yet anything else that handles commands
        return []

    def _dispatch_event(self, event: events.Event):
        # NOTE: When passing the class instance variables (e.g. external_publisher)
        #       it's important to qualify access via the class name instead
        #       of the instance.  Otherwise you will get a TypeError about number of
        #       positional arguments when trying to call it.
        if isinstance(event, events.Deallocated):
            remove_allocation_from_read_model(event, self.uow)
        elif isinstance(event, events.Allocated):
            publish_allocated_event(event, TheExternalWorld.external_publisher)
            add_allocation_to_read_model(event, self.uow)
        elif isinstance(event, events.OutOfStock):
            send_out_of_stock_notification(event, TheExternalWorld.notifications)
        else:
            logger.debug("Don't know what to do with %s" % event)

        return self.uow.collect_new_events()


class InvalidSku(Exception):
    pass

def add_batch(
        cmd: commands.CreateBatch, uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        product = uow.products.get(sku=cmd.sku)
        if product is None:
            product = model.Product(cmd.sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(
            cmd.ref, cmd.sku, cmd.qty, cmd.eta
        ))
        uow.commit()


def allocate(
        cmd: commands.Allocate, uow: unit_of_work.AbstractUnitOfWork
):
    line = OrderLine(cmd.orderid, cmd.sku, cmd.qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f'Invalid sku {line.sku}')
        product.allocate(line)
        uow.commit()


def reallocate(
        event: events.Deallocated, uow: unit_of_work.AbstractUnitOfWork
):
    allocate(commands.Allocate(**asdict(event)), uow=uow)


def change_batch_quantity(
        cmd: commands.ChangeBatchQuantity, uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        product = uow.products.get_by_batchref(batchref=cmd.ref)
        product.change_batch_quantity(ref=cmd.ref, qty=cmd.qty)
        uow.commit()


#pylint: disable=unused-argument

def send_out_of_stock_notification(
        event: events.OutOfStock, notifications: notifications.AbstractNotifications,
):
    notifications.send(
        'stock@made.com',
        f'Out of stock for {event.sku}',
    )


def publish_allocated_event(
        event: events.Allocated, publish: Callable,
):
    publish('line_allocated', event)


def add_allocation_to_read_model(
        event: events.Allocated, uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            'INSERT INTO allocations_view (orderid, sku, batchref)'
            ' VALUES (:orderid, :sku, :batchref)',
            dict(orderid=event.orderid, sku=event.sku, batchref=event.batchref)
        )
        uow.commit()


def remove_allocation_from_read_model(
        event: events.Deallocated, uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            'DELETE FROM allocations_view '
            ' WHERE orderid = :orderid AND sku = :sku',
            dict(orderid=event.orderid, sku=event.sku)
        )
        uow.commit()


