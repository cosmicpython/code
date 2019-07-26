import pytest
from ..random_refs import random_batchref, random_orderid, random_sku
from . import api_client


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_batch():
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    api_client.post_to_add_batch(laterbatch, sku, 100, "2011-01-02")
    api_client.post_to_add_batch(earlybatch, sku, 100, "2011-01-01")
    api_client.post_to_add_batch(otherbatch, othersku, 100, None)

    response = api_client.post_to_allocate(random_orderid(), sku, qty=3)

    assert response.status_code == 201
    assert response.json()["batchref"] == earlybatch


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, orderid = random_sku(), random_orderid()

    response = api_client.post_to_allocate(
        orderid,
        unknown_sku,
        qty=20,
        expect_success=False,
    )

    assert response.status_code == 400
    assert response.json()["message"] == f"Invalid sku {unknown_sku}"
