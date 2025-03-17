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
import usb_midi
from adafruit_seesaw import seesaw, rotaryio, digitalio
from adafruit_debouncer import Debouncer, Button
from adafruit_ht16k33 import segments
from bitarray import bitarray
from TLC5916 import TLC5916
import struct
import microcontroller
import neopixel

print("test")

class stepper:
    def __init__(self, num_steps, neopixel_pin):
        self.current_step = 0
        self.first_step = 0
        self.last_step = num_steps - 1
        self.stepping_forward = True
        self.num_steps = num_steps
        self.neopixel_pin = neopixel_pin

        self.CURRENT_COLOR = (255, 0, 0)
        self.ACTIVE_COLOR = (0, 255, 0)
        self.OFF = (0, 0, 0)

        self.pixels = neopixel.NeoPixel(pin = neopixel_pin, n = num_steps, brightness = .25)

    def advance_step(self):
        self.pixels[self.current_step] = self.OFF

        if self.stepping_forward:
            if self.current_step < self.last_step:
                self.current_step = self.current_step + 1
            else:
                self.current_step = self.first_step
        else:
            if self.current_step > self.first_step:
                self.current_step = self.current_step - 1
            else:
                self.current_step = self.last_step

        
        self.pixels[self.current_step] = self.CURRENT_COLOR

        return self.current_step

    def reverse(self):
        self.stepping_forward = not self.stepping_forward

    def reset(self):
        self.current_step = self.first_step

    def adjust_range_start(self, adjustment):
        # keep adjustment in the range where self.first_step >= 0 and
        # self.last_step < self.num_steps
        #adjustment = max(adjustment, -self.first_step)
        #adjustment = min(adjustment, self.num_steps - 1 - self.last_step)

        if (self.first_step + adjustment) <= 7 and self.first_step + adjustment >= 0:
            self.first_step += adjustment

        if (self.last_step + adjustment) <= 7 and self.last_step + adjustment >= 0:
            self.last_step += adjustment

        self.pixels[first_step] = self.ACTIVE_COLOR

        print(f"adjust_range_start 1st step={self.first_step},last={self.last_step}, adjustment={adjustment}")
        # TODO: self.current_step might be out of range; leave that
        # as is; advance_step() will move it into the right range
        # eventually. We might want to revisit this.

    def adjust_range_length(self, adjustment):
        # keep adjustment in the range where self.first_step <= self.last_step and
        # self.last_step < self.num_steps
        #adjustment = max(adjustment, self.first_step - self.last_step)
        #adjustment = min(adjustment, self.last_step - 1 - self.first_step)
        if (self.last_step + adjustment) <= 7 and self.last_step + adjustment >= 0:
            self.last_step += adjustment

        print(f"adjust_range_length 1st step = {self.first_step} last = {self.last_step}, adjustment = {adjustment}")
         # TODO: self.current_step might be out of range; leave that
        # as is; advance_step() will move it into the right range
        # eventually. We might want to revisit this.

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

# define I2C
i2c = board.STEMMA_I2C()

num_steps = 8  # number of steps/switches per row
steps_per_beat = 4  # subdivide beats down to to 16th notes
# Beat timing assumes 4/4 time signature,
# e.g. 4 beats per measure, 1/4 note gets the beat
set_bpm(120)

# Number of steps and GPIO pin for step LED
stepper = stepper(num_steps, board.D7)

playing = False

# Setup button
start_button_in = DigitalInOut(board.A2)
start_button_in.pull = Pull.UP
start_button = Debouncer(start_button_in)

# Reverse button
reverse_button_in = DigitalInOut(board.A1)
reverse_button_in.pull = Pull.UP
reverse_button = Debouncer(reverse_button_in)

#channel 1 button
button1_in = DigitalInOut(board.D9) 
button1_in.pull = Pull.UP
button1 = Button(button1_in, value_when_pressed=False)

#channel 2 button
button2_in = DigitalInOut(board.D8) 
button2_in.pull = Pull.UP
button2 = Button(button2_in, value_when_pressed=False)

#channel 3 button
button3_in = DigitalInOut(board.A3) 
button3_in.pull = Pull.UP
button3 = Button(button3_in, value_when_pressed=False)

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
tempo_encoder = rotaryio.IncrementalEncoder(rotary_seesaw)
last_tempo_encoder_pos = 0
rotary_seesaw.pin_mode(24, rotary_seesaw.INPUT_PULLUP)  # setup the button pin
knobbutton_in = digitalio.DigitalIO(rotary_seesaw, 24)  # use seesaw digitalio
knobbutton = Debouncer(knobbutton_in)  # create debouncer object for button
tempo_encoder_pos = -tempo_encoder.position


# setup adafruit quad encoder
rotary_seesaw2 = seesaw.Seesaw(i2c, addr=0x49)  # default address is 0x36
   
# Pattern Length Encoder
pattern_length_encoder = rotaryio.IncrementalEncoder(rotary_seesaw2, 1)
last_pattern_length_encoder_pos = 0
pattern_length_encoder_pos = -pattern_length_encoder.position


# Step Shift Encoder
step_shift_encoder = rotaryio.IncrementalEncoder(rotary_seesaw2, 3)
last_step_shift_encoder_pos = 0
step_shift_encoder_pos = -step_shift_encoder.position


# MIDI setup
midi = usb_midi.ports[1]

# default starting sequence
drums = [
    drum("Bass", 36, bitarray([ 0, 0, 0, 0, 0, 0, 0, 0 ])),
    drum("Snar", 38, bitarray([ 0, 0, 0, 0, 0, 0, 0, 0 ])),
    drum("LTom", 41, bitarray([ 0, 0, 0, 0, 0, 0, 0, 0 ])),
    drum("MTom", 44, bitarray([ 0, 0, 0, 0, 0, 0, 0, 0 ])),
    drum("HTom", 56, bitarray([ 0, 0, 0, 0, 0, 0, 0, 0 ])),
]

def play_drum(note):
    midi_msg_on = bytearray([0x90|(channel - 1), note, 120])  # 0x90 is noteon ch 1, 0x99 is noteon ch 10
    midi_msg_off = bytearray([0x80|(channel - 1), note, 0])
    midi.write(midi_msg_on)
    midi.write(midi_msg_off)

def light_steps(drum, step, state):
    # pylint: disable=global-statement
    global leds, num_steps
    remap = [4, 5, 6, 7, 0, 1, 2, 3]
    new_drum = 4 - drum
    new_step = remap[step]
    leds[new_drum * num_steps + new_step] = state
    if state:
        print(f'drum{drum} step{step}: on')
    else:
        print(f'drum{drum} step{step}: off')

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

display = segments.Seg14x4(i2c, address=(0x70))
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

channel= 1

# light up initial LEDs
for drum_index in range(len(drums)):
    drum = drums[drum_index]
    for step_index in range(num_steps):
        light_steps(drum_index, step_index, drum.sequence[step_index])
leds.write()
last_step = ticks_ms()
while True:
    start_button.update()
    if start_button.fell:  # pushed encoder button plays/stops transport
        if playing is True:
            print_sequence()
            save_state()
        playing = not playing
        stepper.reset()
        last_step = int(ticks_add(ticks_ms(), -steps_millis))
        print("*** Play:", playing)

    reverse_button.update()
    if reverse_button.fell:
        stepper.reverse()
 
    button1.update()
    if button1.pressed:
        channel = 1

    button2.update()
    if button2.pressed:
        channel = 2

    button3.update()
    if button3.pressed:
        channel = 3

    if playing:
        now = ticks_ms()
        diff = ticks_diff(now, last_step)
        if diff >= steps_millis:
            late_time = ticks_diff(int(diff), int(steps_millis))
            last_step = ticks_add(now, - late_time//2)

            # TODO: how to display the current step? Separate LED?
            for drum in drums:
                if drum.sequence[stepper.current_step]:  # if there's a 1 at the step for the seq, play it
                    play_drum(drum.note)
            # TODO: how to display the current step? Separate LED?
            stepper.advance_step()
            tempo_encoder_pos = -tempo_encoder.position  # only check encoder while playing between steps
            pattern_length_encoder_pos = -pattern_length_encoder.position
            step_shift_encoder_pos = -step_shift_encoder.position
    else:  # check the encoder all the time when not playing
        tempo_encoder_pos = -tempo_encoder.position
        pattern_length_encoder_pos = -pattern_length_encoder.position
        step_shift_encoder_pos = -step_shift_encoder.position

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

    if tempo_encoder_pos != last_tempo_encoder_pos:
        tempo_encoder_delta = tempo_encoder_pos - last_tempo_encoder_pos
        newbpm = bpm + tempo_encoder_delta  # or (encoder_delta * 5)
        newbpm = min(max(newbpm, 10), 400)
        set_bpm(newbpm)
        display.fill(0)
        display.print(bpm)
        last_tempo_encoder_pos = tempo_encoder_pos

    if pattern_length_encoder_pos != last_pattern_length_encoder_pos:
        pattern_length_encoder_delta = pattern_length_encoder_pos - last_pattern_length_encoder_pos
        stepper.adjust_range_length(pattern_length_encoder_delta)
        last_pattern_length_encoder_pos = pattern_length_encoder_pos
        print(f"last_pattern_length_encoder_pos = {pattern_length_encoder_pos}")

    if step_shift_encoder_pos != last_step_shift_encoder_pos:
        step_shift_encoder_delta = step_shift_encoder_pos - last_step_shift_encoder_pos
        stepper.adjust_range_start(step_shift_encoder_delta)
        last_step_shift_encoder_pos = step_shift_encoder_pos
        print(f"laststep last_step_shift_encoder_pos = {step_shift_encoder_pos}")



 # suppresions:
 # type: ignore
