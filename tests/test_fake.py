from ..src import fake
import digitalio

def test_fake_DigitalInOut_init():
    io = fake.DigitalInOut()
    assert io.__enter__() == io
    assert io.Direction == digitalio.Direction.INPUT
    assert not io.value

def test_fake_DigitalInOut_call():
    io = fake.DigitalInOut()
    assert io() == io.value

def test_fake_DigitalInOut_switch_to_output():
    io = fake.DigitalInOut()
    io.switch_to_output(value = True, drive_mode=digitalio.DriveMode.PUSH_PULL)
    assert io.Direction == digitalio.Direction.OUTPUT
    assert io.value

def test_fake_DigitalInOut_switch_to_input():
    io = fake.DigitalInOut()
    io.switch_to_input(pull = digitalio.Pull.DOWN)
    assert io.Direction == digitalio.Direction.INPUT
    assert io.pull == digitalio.Pull.DOWN

def test_fake_IncrementalEncoder_init():
    enc = fake.IncrementalEncoder()
    assert enc.position == 0

def test_fake_IncrementalEncoder_set_position():
    enc = fake.IncrementalEncoder()
    enc.position = 10
    assert enc.position == 10

def test_HT16K33_init():
    ht = fake.HT16K33()
    assert ht.blink_rate == 0
    assert ht.brightness == 1.0
    assert ht.auto_write == True

def test_HT16K33_set_blink_rate():
    ht = fake.HT16K33()
    ht.blink_rate = 10
    assert ht.blink_rate == 10

def test_HT16K33_brightness_setter():
    ht = fake.HT16K33()
    ht.brightness = 0.5
    assert ht.brightness == 0.5

def test_HT16K33_auto_write_setter():
    ht = fake.HT16K33()
    assert ht.auto_write
    ht.auto_write = False
    assert not ht.auto_write

def test_Seg14x4_init():
    s = fake.Seg14x4()
    assert s.blink_rate == 0
    assert s.brightness == 1.0
    assert s.auto_write == True