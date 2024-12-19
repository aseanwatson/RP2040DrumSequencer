import board
from digitalio import DigitalInOut, Pull, DriveMode, Direction
import keypad
import usb_midi
from adafruit_seesaw import seesaw, rotaryio, digitalio
from adafruit_debouncer import Debouncer
from adafruit_ht16k33 import segments
from TLC5916 import TLC5916
try:
    from typing import Optional,Union,List,Tuple
except:
    pass

class hardware:
    def __init__(self):
        # define I2C
        self.i2c = board.STEMMA_I2C()

        # Start button
        start_button_in = DigitalInOut(board.A2)
        start_button_in.pull = Pull.UP
        self.start_button = Debouncer(start_button_in)

        # Reverse button
        reverse_button_in = DigitalInOut(board.A1)
        reverse_button_in.pull = Pull.UP
        self.reverse_button = Debouncer(reverse_button_in)

        # Setup switches
        self.switches = keypad.ShiftRegisterKeys(
            data = board.SCK,
            latch = board.MOSI,
            clock = board.MISO,
            key_count = 40,
            value_when_pressed = True,
            value_to_latch = True,
            )

        # Setup LEDs
        self.leds = TLC5916(
            oe_pin = board.D5,
            sdi_pin = board.D3,
            clk_pin = board.D2,
            le_pin = board.D4,
            n = 5,
            R_ext=400) # this is what I told Remi to add, but it should be bigger

        # STEMMA QT Rotary encoder setup
        rotary_seesaw = seesaw.Seesaw(self.i2c, addr=0x36)  # default address is 0x36
        self.tempo_encoder = rotaryio.IncrementalEncoder(rotary_seesaw)

        rotary_seesaw.pin_mode(24, rotary_seesaw.INPUT_PULLUP)  # setup the button pin
        knobbutton_in = digitalio.DigitalIO(rotary_seesaw, 24)  # use seesaw digitalio
        self.knobbutton = Debouncer(knobbutton_in)  # create debouncer object for button

        rotary_seesaw2 = seesaw.Seesaw(self.i2c, addr=0x49)  # default address is 0x36
        self.pattern_length_encoder = rotaryio.IncrementalEncoder(rotary_seesaw2, 1)
        self.step_shift_encoder = rotaryio.IncrementalEncoder(rotary_seesaw2, 3)

        # MIDI setup
        self.midi = usb_midi.ports[1]

        # Display
        self.display = segments.Seg14x4(hardware.i2c, address=(0x70))

class fake_DigitalInOut:
    def __init__(self):
        self.Direction = Direction.INPUT
        self.value = False
    def deinit(self) -> None:
        pass
    def __enter__(self):
        return self
    def __exit__(self) -> None:
        pass
    def __call__(self, *args, **kwds):
        return self.value
    def switch_to_output(self, value: bool = False, drive_mode: digitalio.DriveMode = DriveMode.PUSH_PULL) -> None:
        self.Direction = Direction.OUTPUT
        self.drive_mode = drive_mode
    def switch_to_input(self, pull: Optional[Pull] = None) -> None:
        self.Direction = Direction.INPUT
    direction: Direction
    value: bool
    drive_mode: DriveMode
    pull: Optional[Pull]

class fake_IncrementalEncoder:
    def __init__(self):
        self._position = 0
        pass
    @property
    def position(self):
        return self._position
    @position.setter
    def position(self, value):
        self._position = value

class fake_HT16K33:
    def __init__(self) -> None:
        self._blink_rate = 0
        self._brightness = 1.0
        self._auto_write = True
    @property
    def blink_rate(self) -> int:
        return self._blink_rate
    @blink_rate.setter
    def blink_rate(self, rate: int) -> None:
        self._blink_rate = rate
    @property
    def brightness(self) -> float:
        return self._brightness
    @brightness.setter
    def brightness(self, brightness: float) -> None:
        self._brightness = brightness
    @property
    def auto_write(self) -> bool:
        return self._auto_write
    @auto_write.setter
    def auto_write(self, auto_write: bool) -> None:
        self._auto_write = auto_write
    def show(self) -> None:
        pass
    def fill(self, color: bool) -> None:
        pass

class fake_Seg14x4(fake_HT16K33):
    def __init__(self):
        super().__init__()
    def print(self, value: Union[str, float], decimal: int = 0) -> None:
        pass
    def print_hex(self, value: Union[int, str]) -> None:
        pass
    def __setitem__(self, key: int, value: str) -> None:
        pass
    def scroll(self, count: int = 1) -> None:
        pass
    def set_digit_raw(self, index: int, bitmask: Union[int, List[int], Tuple[int, int]]) -> None:
        pass
    def non_blocking_marquee(self, text: str, delay: float = 0.25, loop: bool = True, space_between: bool = False) -> bool:
        return False
    def marquee(self, text: str, delay: float = 0.25, loop: bool = True, space_between=False) -> None:
        pass

class seans_hardware:
    def __init__(self):
        # Start button
        start_button_in = fake_DigitalInOut()
        start_button_in.pull = Pull.UP
        self.start_button = Debouncer(start_button_in)

        # Reverse button
        reverse_button_in = fake_DigitalInOut()
        reverse_button_in.pull = Pull.UP
        self.reverse_button = Debouncer(reverse_button_in)

        # Setup switches
        self.switches = keypad.ShiftRegisterKeys(
            data               = (board.GP15,),
            latch              = board.GP16,
            clock              = board.GP17,
            key_count          = (16,),
            value_when_pressed = True,
            value_to_latch     = True,
            )

        # Setup LEDs
        self.leds = TLC5916(
            oe_pin = board.GP13,
            sdi_pin = board.GP12,
            clk_pin = board.GP11,
            le_pin = board.GP10,
            R_ext= 1100, # two 2.2K resistors in parallel
            n = 2)

        self.tempo_encoder = fake_IncrementalEncoder()
        knobbutton_in = fake_DigitalInOut()
        self.knobbutton = Debouncer(knobbutton_in)  # create debouncer object for button

        self.pattern_length_encoder = fake_IncrementalEncoder()
        self.step_shift_encoder = fake_IncrementalEncoder()

        # MIDI setup
        self.midi = usb_midi.ports[1]

        # Display
        self.display = fake_Seg14x4()