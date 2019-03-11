import model
import repository

def test_repository_can_save_a_batch(session):
    batch = model.Batch('batch1', 'sku1', 100, eta=None)

    repo = repository.BatchRepository(session)
    repo.add(batch)
    session.commit()

    rows = list(session.execute(
        'SELECT reference, sku, _purchased_quantity, eta FROM "batches"')
    )
    assert rows == [('batch1', 'sku1', 100, None)]


def test_repository_can_retrieve_a_batch_with_allocations(session):
    session.execute(
        'INSERT INTO order_lines (orderid, sku, qty) VALUES ("order1", "sku1", 12)'
    )
    [[olid]] = session.execute(
        'SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku',
        dict(orderid='order1', sku='sku1')
    )
    session.execute(
        'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
        ' VALUES ("batch1", "sku1", 100, null)'
    )
    [[b1id]] = session.execute(
        'SELECT id FROM batches WHERE reference=:ref AND sku=:sku',
        dict(ref='batch1', sku='sku1')
    )
    session.execute(
        'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
        ' VALUES ("batch2", "sku1", 100, null)'
    )
    session.execute(
        'INSERT INTO allocations (orderline_id, batch_id) VALUES (:olid, :b1id)',
        dict(olid=olid, b1id=b1id)
    )

    repo = repository.BatchRepository(session)
    retrieved = repo.get('batch1')

    expected = model.Batch('batch1', 'sku1', 100, eta=None)
    expected._allocations = {model.OrderLine('order1', 'sku1', 12)}
    assert retrieved == expected

