import board
from digitalio import DigitalInOut, Pull
import keypad
import usb_midi
from adafruit_seesaw import seesaw, rotaryio, digitalio
from adafruit_debouncer import Debouncer
from adafruit_ht16k33 import segments
from TLC5916 import TLC5916

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
            n = 5)

        # STEMMA QT Rotary encoder setup
        rotary_seesaw = seesaw.Seesaw(hardware.i2c, addr=0x36)  # default address is 0x36
        self.encoder = rotaryio.IncrementalEncoder(rotary_seesaw)

        rotary_seesaw.pin_mode(24, rotary_seesaw.INPUT_PULLUP)  # setup the button pin
        knobbutton_in = digitalio.DigitalIO(rotary_seesaw, 24)  # use seesaw digitalio
        self.knobbutton = Debouncer(knobbutton_in)  # create debouncer object for button

        # MIDI setup
        self.midi = usb_midi.ports[1]

        # Display
        self.display = segments.Seg14x4(hardware.i2c, address=(0x70))
