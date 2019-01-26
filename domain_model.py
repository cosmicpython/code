def skus(d):
    return set(d.keys())

def allocated_completely(order, allocation):
    return skus(order) == skus(allocation)


def allocate_to(order, source):
    return {
        sku: source
        for sku, quantity in order.items()
        if sku in source
        and source[sku] > quantity
    }


def allocate(order, stock, shipments):
    stock_allocation = allocate_to(order, stock)
    if allocated_completely(order, stock_allocation):
        return stock_allocation

    shipment_allocations = []
    for shipment in shipments:
        shipment_allocation = allocate_to(order, shipment)
        if allocated_completely(order, shipment_allocation):
            return shipment_allocation
        shipment_allocations.append(shipment_allocation)

    mixed_allocation = {}
    for allocation in shipment_allocations + [stock_allocation]:
        mixed_allocation.update(allocation)
    return mixed_allocation

