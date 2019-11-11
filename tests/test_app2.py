import pytest
import time

def test_103():
    foo = 'foo'
    time.sleep(1)
    assert 2 == 1

@pytest.mark.voytek
def test_104():
    assert 1 == 1
