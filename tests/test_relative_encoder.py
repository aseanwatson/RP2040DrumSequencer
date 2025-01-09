from ..src import relative_encoder
import rotaryio
import board

def test_relative_encoder():
    enc = rotaryio.IncrementalEncoder(board.D1, board.D2)
    enc.position = 10
    re = relative_encoder.relative_encoder(enc)
    assert re.read_value() == 0
    enc.position = 11
    assert re.read_value() == 1 # 11 -1
    assert re.read_value() == 0
    enc.position = 8 
    assert re.read_value() == -3 # 8 - 11
    assert re.read_value() == 0