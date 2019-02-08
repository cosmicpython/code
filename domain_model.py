def allocate(order, stock, shipments):
    allocations = []
    for source in [stock] + shipments:
        allocation = allocate_to(order, source)
        if allocated_completely(order, allocation):
            return allocation
        allocations.append(allocation)
    return combine_preferring_first(allocations)

def allocate_to(order, source):
    return {
        sku: source
        for sku, quantity in order.items()
        if sku in source
        and source[sku] > quantity
    }

def allocated_completely(order, allocation):
    return order.keys() == allocation.keys()

def combine_preferring_first(allocations):
    return {
        k: v
        for d in reversed(allocations)
        for k, v in d.items()
    }
