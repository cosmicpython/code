from allocation import redis_pubsub

def allocations(orderid):
    batches = redis_pubsub.get_readmodel(orderid)
    return [
        {'batchref': b.decode(), 'sku': s.decode()}
        for s, b in batches.items()
    ]
