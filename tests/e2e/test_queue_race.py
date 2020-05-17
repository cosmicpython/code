from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import json
import pytest
from tenacity import Retrying, RetryError, stop_after_delay
from . import api_client, redis_client
from ..random_refs import random_batchref, random_orderid, random_sku

allocation_events = []

@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
@pytest.mark.usefixtures('restart_redis_pubsub')
def test_parallel_allocation():

    prod = "rug"
    sku = random_sku()

    # Post a large quantity of product, to make sure 
    # we don't run out of allocations
    n_batches = 10
    batch_qty = 10000
    for batch in range(n_batches):
        batch_ref = random_batchref()
        api_client.post_to_add_batch(batch_ref, sku, qty=batch_qty, eta='2020-07-07')

    # Start the queue listener
    subscription = redis_client.subscribe_to('line_allocated')
    thread = threading.Thread(target=listen_for_messages, args=(subscription,))
    thread.start()
    time.sleep(0.2) # *HACK* that gives the thread a chance to start

    # Place a large number of orders with threads
    n_orders = 100
    #n_threads = 20 # will fail
    n_threads = 1 # will pass
    success, failures = place_orders(n_orders, sku, max_workers=n_threads)
    failed_allocations = [int(f.split("-")[1]) for f in failures]

    # Get the number of received allocation events
    thread.join()
    missing_allocation_events = set(range(n_orders)).difference(allocation_events)
    lost_allocation_events = missing_allocation_events.difference(failed_allocations)

    print("Failed to allocate: %d" % len(failed_allocations))
    print(sorted(failed_allocations))

    print("Lost allocation events: %d" % len(lost_allocation_events))
    print(sorted(lost_allocation_events))

    assert lost_allocation_events == set()
    assert missing_allocation_events == set()



def listen_for_messages(subscription):
    """Listen for allocation events, and track order ids"""
    global allocation_events
    while True:
        message = subscription.get_message(timeout=5)
        if message is None:
            break

        data = json.loads(message['data'])
        orderid = data['orderid']
        i = orderid.split('-')[1]
        allocation_events.append(int(i))



def place_orders(norders, sku, max_workers):
    """ Simulate placing a bunch of orders 
        Reutrns a pair of lists. first eleme is successful order ids, second is failed order ids
    """

    order_ids = []
    for i in range(norders):
        prefix = str(i)
        order_ids.append(random_orderid(name=prefix))

    pending = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for order_id in order_ids:
            fut = pool.submit(api_client.post_to_allocate, order_id, sku, qty=1, expect_success=False)
            pending[fut] = order_id
    done, not_done = futures.wait(pending)

    # We expect everything to complete
    assert len(not_done) == 0, "Unexpected failure in test"

    success = []
    failure = []
    for fut in done:
        rsp = fut.result()
        if rsp.status_code == 202:
            success.append(pending[fut])
        else:
            failure.append(pending[fut])

    return success, failure


