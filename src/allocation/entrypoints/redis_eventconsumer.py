import json
import logging
from allocation.adapters import orm, redis_pubsub
from allocation.domain import commands
from allocation.service_layer import messagebus, unit_of_work

logger = logging.getLogger(__name__)


def main():
    orm.start_mappers()
    subscription = redis_pubsub.get_subscription('change_batch_quantity')
    for m in subscription:
        handle_change_batch_quantity(m)


def handle_change_batch_quantity(m):
    logging.debug('handling %s', m)
    data = json.loads(m['data'])
    cmd = commands.ChangeBatchQuantity(ref=data['batchref'], qty=data['qty'])
    messagebus.handle(cmd, uow=unit_of_work.SqlAlchemyUnitOfWork())


if __name__ == '__main__':
    main()
