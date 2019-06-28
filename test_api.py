import uuid
import pytest
import requests

import config


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_batch(add_stock):
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    add_stock(
        [
            (laterbatch, sku, 100, "2011-01-02"),
            (earlybatch, sku, 100, "2011-01-01"),
            (otherbatch, othersku, 100, None),
        ]
    )
    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}
    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batchref"] == earlybatch


@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {"orderid": orderid, "sku": unknown_sku, "qty": 20}
    url = config.get_api_url()
    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_deallocate():
    sku, order1, order2 = random_sku(), random_orderid(), random_orderid()
    batch = random_batchref()
    post_to_add_batch(batch, sku, 100, "2011-01-02")
    url = config.get_api_url()
    # fully allocate
    r = requests.post(
        f"{url}/allocate", json={"orderid": order1, "sku": sku, "qty": 100}
    )
    assert r.json()["batchid"] == batch

    # cannot allocate second order
    r = requests.post(
        f"{url}/allocate", json={"orderid": order2, "sku": sku, "qty": 100}
    )
    assert r.status_code == 400

    # deallocate
    r = requests.post(
        f"{url}/deallocate",
        json={
            "orderid": order1,
            "sku": sku,
        },
    )
    assert r.ok

    # now we can allocate second order
    r = requests.post(
        f"{url}/allocate", json={"orderid": order2, "sku": sku, "qty": 100}
    )
    assert r.ok
    assert r.json()["batchid"] == batch
