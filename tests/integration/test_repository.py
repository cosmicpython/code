# pylint: disable=protected-access
from allocation.domain import model
from allocation.adapters import repository
from allocation import django_model


def test_repository_can_save_a_batch(session):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=date(2011, 12, 25))

    repo = repository.SqlAlchemyRepository(session)
    repo.add(batch)

    [saved_batch] = django_model.Batch.objects.all()
    assert saved_batch.reference == batch.reference
    assert saved_batch.sku == batch.sku
    assert saved_batch.qty == batch.qty
    assert saved_batch.eta == batch.eta


def test_repository_can_retrieve_a_batch_with_allocations(session):
    sku = "PONY-STATUE"
    line = django_model.OrderLine.objects.create(orderid="order1", sku=sku, qty=12)
    django_model.Batch.objects.create(reference="batch1", sku=sku, qty=100, eta=None)
    django_model.Batch.objects.create(reference="batch2", sku=sku, qty=100, eta=None)
    django_model.Allocation.objects.create(
        reference="batch2", sku=sku, qty=100, eta=None
    )

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get("batch1")

    expected = model.Batch("batch1", sku, 100, eta=None)
    assert retrieved == expected  # Batch.__eq__ only compares reference
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {
        model.OrderLine("order1", sku, 12),
    }
