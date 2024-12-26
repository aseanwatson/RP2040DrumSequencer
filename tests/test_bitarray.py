import pytest
from ..src import bitarray

def test_constructor_int():
    ba = bitarray.bitarray(5)
    assert len(ba) == 5
    for i in range(5):
        assert ba[i] == False