import pytest
from ..src import bitarray

@pytest.fixture
def five_element_bitarray_false():
    return bitarray.bitarray(5)

@pytest.fixture
def three_element_bitarray_true_false_true():
    return bitarray.bitarray((True, False, True))

def test_len(three_element_bitarray_true_false_true):
    assert len(three_element_bitarray_true_false_true) == 3

def test_bool_sequence_constructor():
    ba = bitarray.bitarray((True, False, True, False, False))
    assert len(ba) == 5
    assert ba[0]
    assert not ba[1]
    assert ba[2]
    assert not ba[3]
    assert not ba[4]

def test_repr(five_element_bitarray_false):
    assert repr(five_element_bitarray_false) == 'bitarray((0,0,0,0,0))'

def test_getitem(five_element_bitarray_false):
    for i in range(5):
        assert five_element_bitarray_false[i] == False

def test_setitem(five_element_bitarray_false):
    five_element_bitarray_false[1] = True
    five_element_bitarray_false[3] = True
    for i in range(5):
        assert five_element_bitarray_false[i] == bool(i == 1 or i == 3)

def test_toggle(five_element_bitarray_false):
    five_element_bitarray_false.toggle(0)
    assert five_element_bitarray_false[0]
    five_element_bitarray_false.toggle(0)
    assert not five_element_bitarray_false[0]

def test_save_length():
    for i in range(1,300,5):
        ba = bitarray.bitarray(i)
        assert ba.get_save_length() * 8 >= i
        assert ba.get_save_length() * 8 < i + 8

def test_save_state_to_bytes(three_element_bitarray_true_false_true):
    bytecount = three_element_bitarray_true_false_true.get_save_length()
    ba = bytearray(bytecount*2)
    ret = three_element_bitarray_true_false_true.save_state_to_bytes(ba, 0)
    assert ret == bytecount
    ret = three_element_bitarray_true_false_true.save_state_to_bytes(ba, ret)
    assert ret == bytecount
    assert ba == b'\x05\x05'

def test_load_state_from_bytes():
    ba = bitarray.bitarray(16)
    assert ba.get_save_length() == 2
    ba.load_state_from_bytes(b'\x55\x55', 0)
    assert repr(ba) == "bitarray((1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0))"