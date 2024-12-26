import pytest
from ..src import bitarray
from ..src import drum
import usb_midi
from unittest.mock import call,patch

@pytest.fixture
def short_drum():
    return drum.drum("drum name", 10, bitarray.bitarray((1,0,1,0)))

@pytest.fixture
def mock_midi():
    return usb_midi.ports[1]

def test_init(short_drum):
    assert repr(short_drum) == "drum('drum name',10,bitarray((1,0,1,0)))"

def test_play(mock_midi, short_drum):
    short_drum.play(mock_midi, 0)
    mock_midi.write.has_calls([call(b'\x99\x0a\x78'), call(b'\x89\x0a\x00')])
    mock_midi.write.reset_mock()
    short_drum.play(mock_midi, 1)
    mock_midi.write.assert_not_called()
    mock_midi.write.reset_mock()
    short_drum.play(mock_midi, 2)
    mock_midi.write.has_calls([call(b'\x99\x0a\x78'), call(b'\x89\x0a\x00')])
    mock_midi.write.reset_mock()
    short_drum.play(mock_midi, 3)
    mock_midi.write.assert_not_called()
    mock_midi.write.reset_mock()