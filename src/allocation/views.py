from allocation.service_layer import unit_of_work
from sqlalchemy.sql import text


def allocations(orderid: str, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = uow.session.execute(
            text(
                "SELECT sku, batchref FROM allocations_view WHERE orderid = :orderid"
            ),
            dict(orderid=orderid),
        )
    return [r._asdict() for r in results]
