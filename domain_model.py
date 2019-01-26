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


def merge(allocations):
    return {
        k: v
        for d in allocations
        for k, v in d.items()
    }



def allocate(order, stock, shipments):
    allocations = []
    for source in [stock] + shipments:
        allocation = allocate_to(order, source)
        if allocated_completely(order, allocation):
            return allocation
        allocations.append(allocation)

    return merge(reversed(allocations))

