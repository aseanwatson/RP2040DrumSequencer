# SPDX-License-Identifier: MIT
# Drum Trigger Sequencer 2040
# This is a modifiaiton of code by John Park (Adafruit Industries). That code is
# MIT Licensed so this will inherit that license.
# see https://learn.adafruit.com/16-step-drum-sequencer/code-the-16-step-drum-sequencer
# Based on code by Tod Kurt @todbot https://github.com/todbot/picostepseq

# Uses General MIDI drum notes on channel 10
# Range is note 35/B0 - 81/A4, but classic 808 set is defined here

import time
import board
from digitalio import DigitalInOut, Pull
import keypad
import usb_midi
from adafruit_seesaw import seesaw, rotaryio, digitalio
from adafruit_debouncer import Debouncer
from adafruit_ht16k33 import segments
from TLC5916 import TLC5916
from stepper import stepper
import struct
import microcontroller
from drum import drum
from drum_set import drum_set
from ticker import ticker

ticker = ticker(120)

# define I2C
i2c = board.STEMMA_I2C()

num_steps = 8  # number of steps/switches per row

stepper = stepper(num_steps)
playing = False

# Setup button
start_button_in = DigitalInOut(board.A2)
start_button_in.pull = Pull.UP
start_button = Debouncer(start_button_in)

# Reverse button
reverse_button_in = DigitalInOut(board.A1)
reverse_button_in.pull = Pull.UP
reverse_button = Debouncer(reverse_button_in)

# Setup switches
# Input shift register
switches = keypad.ShiftRegisterKeys(
    data = board.SCK,
    latch = board.MOSI,
    clock = board.MISO,
    key_count = 40,
    value_when_pressed = True,
    value_to_latch = True,
    )


# Setup LEDs
# Output shift register
leds = TLC5916(
    oe_pin = board.D5,
    sdi_pin = board.D3,
    clk_pin = board.D2,
    le_pin = board.D4,
    n = 5)

leds.write_config(0)
#
# STEMMA QT Rotary encoder setup
rotary_seesaw = seesaw.Seesaw(i2c, addr=0x36)  # default address is 0x36
encoder = rotaryio.IncrementalEncoder(rotary_seesaw)
last_encoder_pos = 0
rotary_seesaw.pin_mode(24, rotary_seesaw.INPUT_PULLUP)  # setup the button pin
knobbutton_in = digitalio.DigitalIO(rotary_seesaw, 24)  # use seesaw digitalio
knobbutton = Debouncer(knobbutton_in)  # create debouncer object for button
encoder_pos = -encoder.position

# MIDI setup
midi = usb_midi.ports[1]

# default starting sequence
drums = drum_set(midi, num_steps)
drums.add_drum("Bass", 36)
drums.add_drum("Snar", 38)
drums.add_drum("LTom", 41)
drums.add_drum("MTom", 44)
drums.add_drum("HTom", 56)

def light_steps(drum_index: int, step: int, state: bool):
    # pylint: disable=global-statement
    global leds, num_steps
    remap = [4, 5, 6, 7, 0, 1, 2, 3]
    new_drum = 4 - drum_index
    new_step = remap[step]
    leds[new_drum * num_steps + new_step] = state
    if state:
        print(f'drum{drum_index} step{step}: on')
    else:
        print(f'drum{drum_index} step{step}: off')

# format of the header in NVM for save_state/load_state:
# < -- little-endian; lower bits are more significant
# B -- magic number
# B -- number of drums (unsigned byte: 0 - 255)
# B -- number of steps (unsigned byte: 0 - 255)
# H -- BPM beats per minute (unsigned short: 0 - 65536)

# this number should change if load/save logic changes in
# and incompatible way
magic_number = 0x02
class nvm_header:
    format = b'<BBH'
    size = struct.calcsize(format)
    def pack_into(buffer, offset, *v):
        struct.pack_into(nvm_header.format, buffer, offset, *v)
    def unpack_from(buffer, offset = 0):
        return struct.unpack_from(nvm_header.format, buffer, offset)

def save_state() -> None:
    global ticker
    length = nvm_header.size
    for drum in drums:
        length += drum.sequence.bytelen()
    bytes = bytearray(length)
    nvm_header.pack_into(
        bytes,
        0,
        magic_number,
        num_steps,
        ticker.bpm)
    index = nvm_header.size
    for drum in drums:
        drum.sequence.save(bytes, index)
        index += drum.sequence.bytelen()
    # in one update, write the saved bytes
    # to nonvolatile memory
    microcontroller.nvm[0:length] = bytes

def load_state() -> None:
    global num_steps, ticker, drums
    header = nvm_header.unpack_from(microcontroller.nvm[0:nvm_header.size])
    if header[0] != magic_number or header[1] == 0 or header[2] == 0:
        return
    num_steps = header[1]
    newbpm = header[2]
    index = nvm_header.size
    for drum in drums:
        seq = drum.sequence
        seq.load(microcontroller.nvm[index:index+seq.bytelen()])
        index += seq.bytelen()
    ticker.set_bpm(newbpm)

# try to load the state (no-op if NVM not valid)
load_state()

display = segments.Seg14x4(i2c, address=(0x70))
display.brightness = 0.3
display.fill(0)
display.show()
display.print(ticker.bpm)
display.show()

print("Drum Trigger 2040")


display.fill(0)
display.show()
display.marquee("Drum", 0.05, loop=False)
time.sleep(0.5)
display.marquee("Trigger", 0.075, loop=False)
time.sleep(0.5)
display.marquee("2040", 0.05, loop=False)
time.sleep(1)
display.marquee("BPM", 0.05, loop=False)
time.sleep(0.75)
display.marquee(str(ticker.bpm), 0.1, loop=False)

# light up initial LEDs
for drum_index in range(len(drums)):
    drum = drums[drum_index]
    for step_index in range(num_steps):
        light_steps(drum_index, step_index, drum.sequence[step_index])
leds.write()
while True:
    start_button.update()
    if start_button.fell:  # pushed encoder button plays/stops transport
        if playing is True:
            drums.print_sequence()
            save_state()
        playing = not playing
        stepper.reset()
        ticker.restart()
        print("*** Play:", playing)

    reverse_button.update()
    if reverse_button.fell:
        stepper.reverse()

    if playing:
        if ticker.advance():
            # TODO: how to display the current step? Separate LED?
            drums.play_step(stepper.current_step)
            stepper.advance_step()
            encoder_pos = -encoder.position  # only check encoder while playing between steps
    else:  # check the encoder all the time when not playing
        encoder_pos = -encoder.position

    # switches add or remove steps
    switch = switches.events.get()
    if switch:
        if switch.pressed:
            i = switch.key_number
            print(f"key pressed: {i}")
            drum_index = i // num_steps
            step_index = i % num_steps
            drum = drums[drum_index]
            drum.sequence.toggle(step_index) # toggle step
            light_steps(drum_index, step_index, drum.sequence[step_index])  # toggle light
            leds.write()

    if encoder_pos != last_encoder_pos:
        encoder_delta = encoder_pos - last_encoder_pos
        ticker.adjust_bpm(encoder_delta)
        display.fill(0)
        display.print(ticker.bpm)
        last_encoder_pos = encoder_pos

 # suppresions:
 # type: ignore
