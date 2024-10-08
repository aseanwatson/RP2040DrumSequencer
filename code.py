# SPDX-License-Identifier: MIT
# Drum Trigger Sequencer 2040
# This is a modifiaiton of code by John Park (Adafruit Industries). That code is
# MIT Licensed so this will inherit that license.
# see https://learn.adafruit.com/16-step-drum-sequencer/code-the-16-step-drum-sequencer
# Based on code by Tod Kurt @todbot https://github.com/todbot/picostepseq

# Uses General MIDI drum notes on channel 10
# Range is note 35/B0 - 81/A4, but classic 808 set is defined here

import time
from adafruit_ticks import ticks_ms, ticks_diff, ticks_add
import board
from digitalio import DigitalInOut, Pull
import keypad
import adafruit_aw9523
import usb_midi
from adafruit_seesaw import seesaw, rotaryio, digitalio
from adafruit_debouncer import Debouncer
from adafruit_ht16k33 import segments
from bitarray import bitarray
import struct
import microcontroller

class drum:
    def __init__(self, name, note, sequence):
        self.name = name
        self.note = note
        self.sequence = sequence
    
    def __repr__(self):
        return f'drum({repr(self.name)},{repr(self.note)},{repr(self.sequence)})'

def set_bpm(newbpm: int):
    global bpm, steps_millis
    bpm = newbpm
    beat_time = 60/bpm  # time length of a single beat
    beat_millis = beat_time * 1000
    steps_millis = beat_millis / steps_per_beat

def set_drum_index(index: int):
    global drum_index,curr_drum
    drum_index = index % len(drums)
    curr_drum = drums[drum_index]
    # set the leds
    for j in range(num_steps):
        light_steps(j, curr_drum.sequence[j])

# define I2C
i2c = board.STEMMA_I2C()

num_steps = 16  # number of steps/switches
steps_per_beat = 4  # subdivide beats down to to 16th notes
# Beat timing assumes 4/4 time signature, e.g. 4 beats per measure, 1/4 note gets the beat
set_bpm(120)

step_counter = 0  # goes from 0 to length of sequence - 1
playing = False

# Setup button
start_button_in = DigitalInOut(board.A2)
start_button_in.pull = Pull.UP
start_button = Debouncer(start_button_in)


# Setup switches
switch_pins = (
                board.TX, board.RX, board.D2, board.D3,
                board.D4, board.D5, board.D6, board.D7,
                board.D8, board.D9, board.D10, board.MOSI,
                board.MISO, board.SCK, board.A0, board.A1
)
switches = keypad.Keys(switch_pins, value_when_pressed=False, pull=True)

# Setup LEDs
leds = adafruit_aw9523.AW9523(i2c, address=0x5B)  # both jumperes soldered on board
for led in range(num_steps):  # turn them off
    leds.set_constant_current(led, 0)
leds.LED_modes = 0xFFFF  # constant current mode
leds.directions = 0xFFFF  # output

# Values for LED brightness 0-255
offled = 0
dimled = 2
midled = 20
highled = 150

for led in range(num_steps):  # dramatic boot up light sequence
    leds.set_constant_current(led, dimled)
    time.sleep(0.05)
time.sleep(0.5)
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
drums = [
    drum("Bass", 36, bitarray([ 1, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0,  0, 0, 0, 0 ])),
    drum("Snar", 38, bitarray([ 0, 0, 0, 0,  1, 0, 0, 0,  0, 0, 0, 0,  1, 0, 0, 0 ])),
    drum("LTom", 41, bitarray([ 1, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 0, 0 ])),
    drum("MTom", 43, bitarray([ 0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 1, 0 ])),
    drum("HTom", 45, bitarray([ 0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 1 ])),
    drum("Clav", 37, bitarray([ 0, 1, 1, 1,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0 ])),
    drum("Clap", 39, bitarray([ 0, 0, 0, 1,  0, 0, 0, 0,  0, 0, 0, 0,  1, 1, 1, 0 ])),
    drum("Cowb", 56, bitarray([ 0, 0, 0, 0,  0, 1, 0, 1,  1, 0, 1, 0,  0, 0, 0, 0 ])),
    drum("Cymb", 49, bitarray([ 1, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0 ])),
    drum("OHat", 46, bitarray([ 0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 1, 0, 0 ])),
    drum("CHat", 42, bitarray([ 0, 0, 0, 0,  0, 1, 1, 1,  0, 1, 1, 1,  0, 0, 1, 0 ])),
]

def play_drum(note):
    midi_msg_on = bytearray([0x99, note, 120])  # 0x90 is noteon ch 1, 0x99 is noteon ch 10
    midi_msg_off = bytearray([0x89, note, 0])
    midi.write(midi_msg_on)
    midi.write(midi_msg_off)

def light_steps(step, state):
    if state:
        leds.set_constant_current(step, midled)
    else:
        leds.set_constant_current(step, offled)

def light_beat(step):
    leds.set_constant_current(step, highled)

def edit_mode_toggle():
    # pylint: disable=global-statement
    global edit_mode
    # pylint: disable=used-before-assignment
    edit_mode = (edit_mode + 1) % num_modes
    display.fill(0)
    if edit_mode == 0:
        display.print(bpm)
    elif edit_mode == 1:
        display.print(curr_drum.name)

def print_sequence():
    print("drums = [ ")
    for drum in drums:
        print(" " + repr(drum) + ",")
    print("]")

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
    length = nvm_header.size
    for drum in drums:
        length += drum.sequence.bytelen()
    bytes = bytearray(length)
    nvm_header.pack_into(
        bytes,
        0,
        magic_number,
        num_steps,
        bpm)
    index = nvm_header.size
    for drum in drums:
        drum.sequence.save(bytes, index)
        index += drum.sequence.bytelen()
    # in one update, write the saved bytes
    # to nonvolatile memory
    microcontroller.nvm[0:length] = bytes

def load_state() -> None:
    global num_steps, bpm, steps_millis
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
    set_bpm(newbpm)

# try to load the state (no-op if NVM not valid)
load_state()

# set the current drum
set_drum_index(0)

display = segments.Seg14x4(i2c, address=(0x71))
display.brightness = 0.3
display.fill(0)
display.show()
display.print(bpm)
display.show()

edit_mode = 0  # 0=bpm, 1=voices
num_modes = 2

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
display.marquee(str(bpm), 0.1, loop=False)


while True:
    start_button.update()
    if start_button.fell:  # pushed encoder button plays/stops transport
        if playing is True:
            print_sequence()
            save_state()
        playing = not playing
        step_counter = 0
        last_step = int(ticks_add(ticks_ms(), -steps_millis))
        print("*** Play:", playing)

    if playing:
        now = ticks_ms()
        diff = ticks_diff(now, last_step)
        if diff >= steps_millis:
            late_time = ticks_diff(int(diff), int(steps_millis))
            last_step = ticks_add(now, - late_time//2)

            light_beat(step_counter)  # brighten current step
            for drum in drums:
                if drum.sequence[step_counter]:  # if there's a 1 at the step for the seq, play it
                    play_drum(drums.note)
            light_steps(step_counter, curr_drum.sequence[step_counter])  # return led to step value
            step_counter = (step_counter + 1) % num_steps
            encoder_pos = -encoder.position  # only check encoder while playing between steps
            knobbutton.update()
            if knobbutton.fell:
                edit_mode_toggle()
    else:  # check the encoder all the time when not playing
        encoder_pos = -encoder.position
        knobbutton.update()
        if knobbutton.fell:  # change edit mode, refresh display
            edit_mode_toggle()

    # switches add or remove steps
    switch = switches.events.get()
    if switch:
        if switch.pressed:
            i = switch.key_number
            curr_drum.sequence.toggle(i) # toggle step
            light_steps(i, curr_drum.sequence[i])  # toggle light

    if encoder_pos != last_encoder_pos:
        encoder_delta = encoder_pos - last_encoder_pos
        if edit_mode == 0:
            newbpm = bpm + encoder_delta  # or (encoder_delta * 5)
            newbpm = min(max(newbpm, 10), 400)
            set_bpm(newbpm)
            display.fill(0)
            display.print(bpm)
        if edit_mode == 1:
            set_drum_index(drum_index + encoder_delta)
            display.print(curr_drum.name)
        last_encoder_pos = encoder_pos

 # suppresions:
 # type: ignore