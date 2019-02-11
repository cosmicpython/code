from domain_model import Order, Warehouse, Shipment
from datetime import date, timedelta

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_can_allocate_to_warehouse():
    order = Order({'a-sku': 10})
    warehouse = Warehouse({'a-sku': 1000})

    order.allocate(warehouse, shipments=[])

    assert order.allocation['a-sku'] == warehouse
    assert warehouse['a-sku'] == 990


def test_can_allocate_to_shipment():
    order = Order({'a-sku': 10})
    shipment = Shipment({'a-sku': 1000}, eta=tomorrow)

    order.allocate(warehouse=Warehouse({}), shipments=[shipment])

    assert order.allocation['a-sku'] == shipment
    assert shipment['a-sku'] == 990


def test_ignores_irrelevant_warehouse():
    order = Order({'sku1': 10})
    warehouse = Warehouse({'sku2': 1000})
    shipment = Shipment({'sku1': 1000}, eta=tomorrow)

    order.allocate(warehouse=warehouse, shipments=[shipment])

    assert order.allocation['sku1'] == shipment



def test_can_allocate_to_correct_shipment():
    order = Order({'sku2': 10})
    shipment1 = Shipment({'sku1': 1000}, eta=tomorrow)
    shipment2 = Shipment({'sku2': 1000}, eta=tomorrow)

    order.allocate(warehouse=Warehouse({}), shipments=[shipment1, shipment2])

    assert order.allocation['sku2'] == shipment2


def test_allocates_to_warehouse_in_preference_to_shipment():
    order = Order({'sku1': 10})
    warehouse = Warehouse({'sku1': 1000})
    shipment = Shipment({'sku1': 1000}, eta=tomorrow)

    order.allocate(warehouse, shipments=[shipment])

    assert order.allocation['sku1'] == warehouse
    assert warehouse['sku1'] == 990
    assert shipment['sku1'] == 1000


def test_can_allocate_multiple_lines_to_wh():
    order = Order({'sku1': 5, 'sku2': 10})
    warehouse = Warehouse({'sku1': 1000, 'sku2': 1000})

    order.allocate(warehouse, shipments=[])
    assert order.allocation['sku1'] == warehouse
    assert order.allocation['sku2'] == warehouse
    assert warehouse['sku1'] == 995
    assert warehouse['sku2'] == 990


def test_can_allocate_multiple_lines_to_shipment():
    order = Order({'sku1': 5, 'sku2': 10})
    shipment = Shipment({'sku1': 1000, 'sku2': 1000}, eta=tomorrow)

    order.allocate(warehouse=Warehouse({}), shipments=[shipment])

    assert order.allocation['sku1'] == shipment
    assert order.allocation['sku2'] == shipment
    assert shipment['sku1'] == 995
    assert shipment['sku2'] == 990


def test_can_allocate_to_both():
    order = Order({'sku1': 5, 'sku2': 10})
    shipment = Shipment({'sku2': 1000}, eta=tomorrow)
    warehouse = Warehouse({'sku1': 1000})

    order.allocate(warehouse, shipments=[shipment])

    assert order.allocation['sku1'] == warehouse
    assert order.allocation['sku2'] == shipment
    assert warehouse['sku1'] == 995
    assert shipment['sku2'] == 990


def test_can_allocate_to_both_preferring_warehouse():
    order = Order({'sku1': 1, 'sku2': 2, 'sku3': 3, 'sku4': 4})
    shipment = Shipment({'sku1': 1000, 'sku2': 1000, 'sku3': 1000}, eta=tomorrow)
    warehouse = Warehouse({'sku3': 1000, 'sku4': 1000})

    order.allocate(warehouse, shipments=[shipment])

    assert order.allocation['sku1'] == shipment
    assert order.allocation['sku2'] == shipment
    assert order.allocation['sku3'] == warehouse
    assert order.allocation['sku4'] == warehouse
    assert shipment['sku1'] == 999
    assert shipment['sku2'] == 998
    assert shipment['sku3'] == 1000
    assert warehouse['sku3'] == 997
    assert warehouse['sku4'] == 996


def test_allocated_to_earliest_suitable_shipment_in_list():
    order = Order({'sku1': 10, 'sku2': 10})
    shipment1 = Shipment({'sku1': 1000, 'sku2': 1000}, eta=today)
    shipment2 = Shipment({'sku1': 1000, 'sku2': 1000}, eta=tomorrow)
    warehouse = Warehouse({})

    order.allocate(warehouse, shipments=[shipment1, shipment2])

    assert order.allocation['sku1'] == shipment1
    assert order.allocation['sku2'] == shipment1


def test_still_chooses_earliest_if_split_across_shipments():
    order = Order({'sku1': 10, 'sku2': 10, 'sku3': 10})
    shipment1 = Shipment({'sku1': 1000}, eta=today)
    shipment2 = Shipment({'sku2': 1000, 'sku3': 1000}, eta=tomorrow)
    shipment3 = Shipment({'sku2': 1000, 'sku3': 1000}, eta=later)
    warehouse = Warehouse({})

    order.allocate(warehouse, shipments=[shipment2, shipment3, shipment1])

    assert order.allocation['sku1'] == shipment1
    assert order.allocation['sku2'] == shipment2
    assert order.allocation['sku3'] == shipment2


def test_warehouse_not_quite_enough_means_we_use_shipment():
    order = Order({'sku1': 10, 'sku2': 10})
    warehouse = Warehouse({'sku1': 10, 'sku2': 5})
    shipment = Shipment({
        'sku1': 1000,
        'sku2': 1000,
    }, eta=tomorrow)

    order.allocate(warehouse, shipments=[shipment])

    assert order.allocation['sku1'] == shipment
    assert order.allocation['sku2'] == shipment


def test_cannot_allocate_if_insufficent_quantity_in_warehouse():
    order = Order({'a-sku': 10})
    warehouse = Warehouse({'a-sku': 5})

    order.allocate(warehouse, shipments=[])

    assert 'a-sku' not in order.allocation


def test_cannot_allocate_if_insufficent_quantity_in_shipment():
    order = Order({'a-sku': 10})
    shipment = Shipment({'a-sku': 5}, eta=tomorrow)

    order.allocate(warehouse=Warehouse({}), shipments=[shipment])

    assert 'a-sku' not in order.allocation

