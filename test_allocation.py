from domain_model import allocate


def test_can_allocate_to_warehouse():
    order = {'a-sku': 10}
    warehouse = {'a-sku': 1000}

    allocations = allocate(order, warehouse, shipments=[])

    assert allocations['a-sku'] == warehouse


def test_can_allocate_to_shipment():
    order = {'a-sku': 10}
    shipment = {'a-sku': 1000}

    allocations = allocate(order, warehouse={}, shipments=[shipment])

    assert allocations['a-sku'] == shipment


def test_ignores_irrelevant_warehouse_stock():
    order = {'sku1': 10}
    warehouse = {'sku2': 1000}
    shipment = {'sku1': 1000}

    allocations = allocate(order, warehouse=warehouse, shipments=[shipment])

    assert allocations['sku1'] == shipment


def test_can_allocate_to_correct_shipment():
    order = {'sku2': 10}
    shipment1 = {'sku1': 1000}
    shipment2 = {'sku2': 1000}

    allocations = allocate(order, warehouse={}, shipments=[shipment1, shipment2])

    assert allocations['sku2'] == shipment2


def test_allocates_to_warehouse_in_preference_to_shipment():
    order = {'sku1': 10}
    warehouse = {'sku1': 1000}
    shipment = {'sku1': 1000}

    allocations = allocate(order, warehouse, shipments=[shipment])

    assert allocations['sku1'] == warehouse


def test_can_allocate_multiple_lines_to_warehouse():
    order = {'sku1': 5, 'sku2': 10}
    warehouse = {'sku1': 1000, 'sku2': 1000}

    allocations = allocate(order, warehouse, shipments=[])
    assert allocations['sku1'] == warehouse
    assert allocations['sku2'] == warehouse


def test_can_allocate_multiple_lines_to_shipment():
    order = {'sku1': 5, 'sku2': 10}
    shipment = {'sku1': 1000, 'sku2': 1000}

    allocations = allocate(order, warehouse={}, shipments=[shipment])

    assert allocations['sku1'] == shipment
    assert allocations['sku2'] == shipment


def test_can_allocate_to_both():
    order = {'sku1': 5, 'sku2': 10}
    shipment = {'sku2': 1000}
    warehouse = {'sku1': 1000}

    allocations = allocate(order, warehouse, shipments=[shipment])

    assert allocations['sku1'] == warehouse
    assert allocations['sku2'] == shipment


def test_can_allocate_to_both_preferring_warehouse():
    order = {'sku1': 1, 'sku2': 2, 'sku3': 3, 'sku4': 4}
    shipment = {'sku1': 1000, 'sku2': 1000, 'sku3': 1000}
    warehouse = {'sku3': 1000, 'sku4': 1000}

    allocations = allocate(order, warehouse, shipments=[shipment])

    assert allocations['sku1'] == shipment
    assert allocations['sku2'] == shipment
    assert allocations['sku3'] == warehouse
    assert allocations['sku4'] == warehouse


def test_allocated_to_first_suitable_shipment_in_list():
    order = {'sku1': 10, 'sku2': 10}
    shipment1 = {'sku1': 1000, 'sku2': 1000}
    shipment2 = {'sku1': 1000, 'sku2': 1000}
    warehouse = {}

    allocations = allocate(order, warehouse, shipments=[shipment1, shipment2])

    assert allocations['sku1'] == shipment1
    assert allocations['sku2'] == shipment1


def test_still_preserves_ordering_if_split_across_shipments():
    order = {'sku1': 10, 'sku2': 10, 'sku3': 10}
    shipment1 = {'sku1': 1000}
    shipment2 = {'sku2': 1000, 'sku3': 1000}
    shipment3 = {'sku2': 1000, 'sku3': 1000}
    warehouse = {}

    allocations = allocate(order, warehouse, shipments=[shipment1, shipment2, shipment3])

    assert allocations['sku1'] == shipment1
    assert allocations['sku2'] == shipment2
    assert allocations['sku3'] == shipment2


def test_warehouse_not_quite_enough_means_we_use_shipment():
    order = {'sku1': 10, 'sku2': 10}
    warehouse = {'sku1': 10, 'sku2': 5}
    shipment = {
        'sku1': 1000,
        'sku2': 1000,
    }

    allocations = allocate(order, warehouse, shipments=[shipment])

    assert allocations['sku1'] == shipment
    assert allocations['sku2'] == shipment


def test_cannot_allocate_if_insufficent_quantity_in_warehouse():
    order = {'a-sku': 10}
    warehouse = {'a-sku': 5}

    allocations = allocate(order, warehouse, shipments=[])

    assert 'a-sku' not in allocations


def test_cannot_allocate_if_insufficent_quantity_in_shipment():
    order = {'a-sku': 10}
    shipment = {
        'a-sku': 5,
    }

    allocations = allocate(order, warehouse={}, shipments=[shipment])

    assert 'a-sku' not in allocations

