import microcontroller
import adafruit_seesaw.rotaryio
import pytest
from unittest.mock import call,patch,MagicMock

from ..src import sequencer
from ..src import hardware

@pytest.fixture
def mock_sequencer() -> sequencer.sequencer:
    adafruit_seesaw.rotaryio.IncrementalEncoder.return_value = MagicMock(position=0)
    retval = sequencer.sequencer(bpm=100)
    return retval

def test_sequencer_init(mock_sequencer: sequencer.sequencer):
    num_steps = mock_sequencer.hardware.num_steps
    assert num_steps == 8
    assert mock_sequencer.ticker.bpm == 100
    assert not mock_sequencer.ticker.playing
    assert mock_sequencer.stepper.current_step == 0
    assert mock_sequencer.stepper.first_step == 0
    assert mock_sequencer.stepper.last_step == num_steps - 1
    assert mock_sequencer.tempo_encoder.position == 0

def test_sequener_setup(mock_sequencer):
    with (patch.object(
            target=microcontroller.nvm,
            attribute='__getitem__',
            return_value=bytearray(1000))):
        mock_sequencer.setup()

def test_sequencer_nonloop(mock_sequencer: sequencer.sequencer):
    with (patch.object(
            target=mock_sequencer.hardware.switches.events,
            attribute='get',
            return_value = None),
        patch.object(
            target=microcontroller.nvm,
            attribute='__getitem__',
            return_value=bytearray(1000))):
        mock_sequencer.setup()
        mock_sequencer.run_main_loop()