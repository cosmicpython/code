from domain_model import Order, Stock
from datetime import date, timedelta

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_can_allocate_to_stock():
    order = Order({'a-sku': 10})
    stock = Stock({'a-sku': 1000})

    order.allocate(stock, shipments=[])

    assert order.allocation['a-sku'] == stock


def test_can_allocate_to_shipment():
    order = Order({'a-sku': 10})
    shipment = Stock({'a-sku': 1000}, eta=tomorrow)

    order.allocate(stock=Stock({}), shipments=[shipment])

    assert order.allocation['a-sku'] == shipment


def test_ignores_irrelevant_stock():
    order = Order({'sku1': 10})
    stock = Stock({'sku2': 1000})
    shipment = Stock({'sku1': 1000}, eta=tomorrow)

    order.allocate(stock=stock, shipments=[shipment])

    assert order.allocation['sku1'] == shipment



def test_can_allocate_to_correct_shipment():
    order = Order({'sku2': 10})
    shipment1 = Stock({'sku1': 1000}, eta=tomorrow)
    shipment2 = Stock({'sku2': 1000}, eta=tomorrow)

    order.allocate(stock=Stock({}), shipments=[shipment1, shipment2])

    assert order.allocation['sku2'] == shipment2


def test_allocates_to_stock_in_preference_to_shipment():
    order = Order({'sku1': 10})
    stock = Stock({'sku1': 1000})
    shipment = Stock({'sku1': 1000}, eta=tomorrow)

    order.allocate(stock, shipments=[shipment])

    assert order.allocation['sku1'] == stock


def test_can_allocate_multiple_lines_to_wh():
    order = Order({'sku1': 5, 'sku2': 10})
    stock = Stock({'sku1': 1000, 'sku2': 1000})

    order.allocate(stock, shipments=[])
    assert order.allocation['sku1'] == stock
    assert order.allocation['sku2'] == stock


def test_can_allocate_multiple_lines_to_shipment():
    order = Order({'sku1': 5, 'sku2': 10})
    shipment = Stock({'sku1': 1000, 'sku2': 1000}, eta=tomorrow)

    order.allocate(stock=Stock({}), shipments=[shipment])

    assert order.allocation['sku1'] == shipment
    assert order.allocation['sku2'] == shipment


def test_can_allocate_to_both():
    order = Order({'sku1': 5, 'sku2': 10})
    shipment = Stock({'sku2': 1000}, eta=tomorrow)
    stock = Stock({'sku1': 1000})

    order.allocate(stock, shipments=[shipment])

    assert order.allocation['sku1'] == stock
    assert order.allocation['sku2'] == shipment


def test_can_allocate_to_both_preferring_stock():
    order = Order({'sku1': 1, 'sku2': 2, 'sku3': 3, 'sku4': 4})
    shipment = Stock({'sku1': 1000, 'sku2': 1000, 'sku3': 1000}, eta=tomorrow)
    stock = Stock({'sku3': 1000, 'sku4': 1000})

    order.allocate(stock, shipments=[shipment])

    assert order.allocation['sku1'] == shipment
    assert order.allocation['sku2'] == shipment
    assert order.allocation['sku3'] == stock
    assert order.allocation['sku4'] == stock


def test_mixed_allocation_are_avoided_if_possible():
    order = Order({'sku1': 10, 'sku2': 10})
    shipment = Stock({'sku1': 1000, 'sku2': 1000}, eta=tomorrow)
    stock = Stock({'sku1': 1000})

    order.allocate(stock, shipments=[shipment])

    assert order.allocation['sku1'] == shipment
    assert order.allocation['sku2'] == shipment


def test_allocated_to_earliest_suitable_shipment_in_list():
    order = Order({'sku1': 10, 'sku2': 10})
    shipment1 = Stock({'sku1': 1000, 'sku2': 1000}, eta=today)
    shipment2 = Stock({'sku1': 1000, 'sku2': 1000}, eta=tomorrow)
    stock = Stock({})

    order.allocate(stock, shipments=[shipment2, shipment1])

    assert order.allocation['sku1'] == shipment1
    assert order.allocation['sku2'] == shipment1


def test_still_chooses_earliest_if_split_across_shipments():
    order = Order({'sku1': 10, 'sku2': 10, 'sku3': 10})
    shipment1 = Stock({'sku1': 1000}, eta=today)
    shipment2 = Stock({'sku2': 1000, 'sku3': 1000}, eta=tomorrow)
    shipment3 = Stock({'sku2': 1000, 'sku3': 1000}, eta=later)
    stock = Stock({})

    order.allocate(stock, shipments=[shipment3, shipment2, shipment1])

    assert order.allocation['sku1'] == shipment1
    assert order.allocation['sku2'] == shipment2
    assert order.allocation['sku3'] == shipment2


def test_stock_not_quite_enough_means_we_use_shipment():
    order = Order({'sku1': 10, 'sku2': 10})
    stock = Stock({'sku1': 10, 'sku2': 5})
    shipment = Stock({
        'sku1': 1000,
        'sku2': 1000,
    })

    order.allocate(stock, shipments=[shipment])

    assert order.allocation['sku1'] == shipment
    assert order.allocation['sku2'] == shipment


def test_cannot_allocate_if_insufficent_quantity_in_stock():
    order = Order({'a-sku': 10})
    stock = Stock({'a-sku': 5})

    order.allocate(stock, shipments=[])

    assert 'a-sku' not in order.allocation


def test_cannot_allocate_if_insufficent_quantity_in_shipment():
    order = Order({'a-sku': 10})
    shipment = Stock({'a-sku': 5}, eta=tomorrow)

    order.allocate(stock=Stock({}), shipments=[shipment])

    assert 'a-sku' not in order.allocation

