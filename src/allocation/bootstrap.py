from typing import Callable
from allocation.domain import commands, events
from allocation.adapters import email, orm, redis_eventpublisher
from allocation.service_layer import handlers, messagebus, unit_of_work


def bootstrap(
    start_orm: bool = True,
    uow: unit_of_work.AbstractUnitOfWork = unit_of_work.SqlAlchemyUnitOfWork(),
    send_mail: Callable = email.send,
    publish: Callable = redis_eventpublisher.publish,
) -> messagebus.MessageBus:

    if start_orm:
        orm.start_mappers()

    injected_event_handlers = {
        events.Allocated: [
            lambda e: handlers.publish_allocated_event(e, publish),
            lambda e: handlers.add_allocation_to_read_model(e, uow),
        ],
        events.Deallocated: [
            lambda e: handlers.remove_allocation_from_read_model(e, uow),
            lambda e: handlers.reallocate(e, uow),
        ],
        events.OutOfStock: [
            lambda e: handlers.send_out_of_stock_notification(e, send_mail)
        ]
    }
    injected_command_handlers = {
        commands.Allocate: lambda c: handlers.allocate(c, uow),
        commands.CreateBatch: \
            lambda c: handlers.add_batch(c, uow),
        commands.ChangeBatchQuantity: \
            lambda c: handlers.change_batch_quantity(c, uow),
    }

    return messagebus.MessageBus(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
    )


def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }
    return lambda message: handler(message, **deps)
