import functools
import inspect
from typing import Callable
from allocation.adapters import orm, redis_eventpublisher
from allocation.adapters.notifications import (
    AbstractNotifications, EmailNotifications
)
from allocation.service_layer import handlers, messagebus, unit_of_work


def bootstrap(
    start_orm: bool = True,
    notifications: AbstractNotifications = None,
    publish: Callable = redis_eventpublisher.publish,
) -> messagebus.MessageBus:

    if notifications is None:
        notifications = EmailNotifications()

    if start_orm:
        orm.start_mappers()

    bus = messagebus.MessageBus()

    # Setup our actors here!
    handlers.TheExternalWorld.notifications = notifications
    handlers.TheExternalWorld.external_publisher = publish

    handlers.TheExternalWorld.register_with(bus)
    handlers.ProductActor.register_with(bus)

    return bus


