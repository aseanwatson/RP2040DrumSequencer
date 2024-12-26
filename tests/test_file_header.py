import pytest
from ..src import file_header

def test_file_header_init():
    fh = file_header.file_header(drum_count=10, step_count=20, bpm=30)
    assert fh.magic_number == file_header.file_header.magic_number
    assert fh.drum_count == 10
    assert fh.step_count == 20
    assert fh.bpm == 30

def test_file_header_save_length():
    fh = file_header.file_header(drum_count=10, step_count=20, bpm=30)
    assert fh.get_save_length() == 5

def test_file_header_load_state_from_bytes():
    fh = file_header.file_header(drum_count=10, step_count=20, bpm=30)
    ret = fh.load_state_from_bytes(b'\x02\x0A\x14\xC8\x00')
    assert ret == 5
    assert fh.bpm == 0x00C8 # 200
    with pytest.raises(ValueError):
        _ = fh.load_state_from_bytes(b'\x03\x0A\x14\xC8\x00')
    with pytest.raises(ValueError):
        _ = fh.load_state_from_bytes(b'\x02\x0B\x14\xC8\x00')
    with pytest.raises(ValueError):
        _ = fh.load_state_from_bytes(b'\x02\x0A\x15\xC8\x00')

def test_file_header_save_state_to_bytes():
    fh = file_header.file_header(drum_count=10, step_count=20, bpm=30)
    ba = bytearray(5)
    ret = fh.save_state_to_bytes(ba, 0)
    assert ret == 5
    assert ba == b'\x02\x0A\x14\x1E\x00'