# SPDX-License-Identifier: MIT
# Drum Trigger Sequencer 2040
# This is a modifiaiton of code by John Park (Adafruit Industries). That code is
# MIT Licensed so this will inherit that license.
# see https://learn.adafruit.com/16-step-drum-sequencer/code-the-16-step-drum-sequencer
# Based on code by Tod Kurt @todbot https://github.com/todbot/picostepseq

# Uses General MIDI drum notes on channel 10
# Range is note 35/B0 - 81/A4, but classic 808 set is defined here

import stepper
import struct
import microcontroller
import drum
import drum_set
import ticker
import hardware
import relative_encoder

hardware = hardware.hardware()
hardware.leds.write_config(0)
hardware.display.brightness = 0.3

num_steps = 8  # number of steps/switches per row

ticker = ticker.ticker(bpm = 120)
stepper = stepper.stepper(num_steps)

# default starting sequence
drums = drum_set.drum_set(hardware.midi, num_steps)
drums.add_drum(drum.BassDrum)
drums.add_drum(drum.AcousticSnare)
drums.add_drum(drum.LowFloorTom)
drums.add_drum(drum.PedalHiHat)
drums.add_drum(drum.CowBell)

def light_steps(drum_index: int, step: int, state: bool):
    # pylint: disable=global-statement
    global hardware, num_steps
    remap = [4, 5, 6, 7, 0, 1, 2, 3]
    new_drum = 4 - drum_index
    new_step = remap[step]
    hardware.leds[new_drum * num_steps + new_step] = state
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

hardware.display.fill(0)
hardware.display.print(ticker.bpm)
hardware.display.show()

# light up initial LEDs
for drum_index in range(len(drums)):
    drum = drums[drum_index]
    for step_index in range(num_steps):
        light_steps(drum_index, step_index, drum.sequence[step_index])
hardware.leds.write()

tempo_encoder = relative_encoder.relative_encoder(hardware.tempo_encoder)
step_shift_encoder = relative_encoder.relative_encoder(hardware.step_shift_encoder)
pattern_length_encoder = relative_encoder.relative_encoder(hardware.pattern_length_encoder)

while True:
    hardware.start_button.update()
    if hardware.start_button.fell:  # pushed encoder button plays/stops transport
        # Toggle playing state
        ticker.toggle_playing()

        if not ticker.playing:
            drums.print_sequence()
            save_state()
        stepper.reset()
        print("*** Play:", ticker.playing)

    hardware.reverse_button.update()
    if hardware.reverse_button.fell:
        stepper.reverse()

    # switches add or remove steps
    switch = hardware.switches.events.get()
    if switch:
        if switch.pressed:
            i = switch.key_number
            print(f"key pressed: {i}")
            drum_index = i // num_steps
            step_index = i % num_steps
            drum = drums[drum_index]
            drum.sequence.toggle(step_index) # toggle step
            light_steps(drum_index, step_index, drum.sequence[step_index])  # toggle light
            hardware.leds.write()

    # TODO: I don't understand why we only want to check the encoder between steps
    check_encoder = not ticker.playing

    if ticker.playing:
        if ticker.advance():
            # TODO: how to display the current step? Separate LED?
            drums.play_step(stepper.current_step)
            stepper.advance_step()
            check_encoder = True

    if check_encoder:
        tempo_encoder_delta = tempo_encoder.read_value()
        if tempo_encoder_delta != 0:
            ticker.adjust_bpm(tempo_encoder_delta)
            hardware.display.fill(0)
            hardware.display.print(ticker.bpm)

        step_shift_encoder_delta = step_shift_encoder.read_value()
        if step_shift_encoder_delta != 0:
            stepper.adjust_range_start(step_shift_encoder_delta)

        pattern_length_encoder_delta = pattern_length_encoder.read_value()
        if pattern_length_encoder_delta != 0:
            stepper.adjust_range_length(pattern_length_encoder_delta)

 # suppresions:
 # type: ignore
