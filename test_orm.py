import model

def test_orderline_mapper_can_load_lines(session):
    session.execute(
        'INSERT INTO order_lines (orderid, sku, qty) VALUES '
        '("order1", "sku1", 12),'
        '("order1", "sku2", 13),'
        '("order2", "sku3", 14)'
    )
    expected = [
        model.OrderLine('order1', 'sku1', 12),
        model.OrderLine('order1', 'sku2', 13),
        model.OrderLine('order2', 'sku3', 14),
    ]
    assert session.query(model.OrderLine).all() == expected


def test_orderline_mapper_can_save_lines(session):
    new_line = model.OrderLine('order1', 'sku1', 12)
    session.add(new_line)
    session.commit()

    rows = list(session.execute('SELECT orderid, sku, qty FROM "order_lines"'))
    assert rows == [('order1', 'sku1', 12)]

