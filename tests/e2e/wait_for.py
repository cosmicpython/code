#pylint: disable=bare-except
import time
import pytest

def wait_for(fn):
    """
    Keep retrying a function, catching any exceptions, until it returns something truthy,
    or we hit a timeout.
    """
    timeout = time.time() + 3
    while time.time() < timeout:
        try:
            r = fn()
            if r:
                return r
        except:
            if time.time() > timeout:
                raise
        time.sleep(0.1)
    pytest.fail(f'function {fn} never returned anything truthy')
