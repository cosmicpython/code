# pylint: disable=redefined-outer-name
import time
from pathlib import Path
import pytest
import requests
from requests.exceptions import ConnectionError
from allocation import config


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../src/djangoproject/manage.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
