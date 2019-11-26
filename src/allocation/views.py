from allocation.adapters import redis_eventpublisher
from allocation.service_layer import unit_of_work

def allocations(orderid):
    batches = redis_eventpublisher.get_readmodel(orderid)
    return [
        {'batchref': b.decode(), 'sku': s.decode()}
        for s, b in batches.items()
    ]
