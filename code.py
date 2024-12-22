# SPDX-License-Identifier: MIT
# Drum Trigger Sequencer 2040
# This is a modifiaiton of code by John Park (Adafruit Industries). That code is
# MIT Licensed so this will inherit that license.
# see https://learn.adafruit.com/16-step-drum-sequencer/code-the-16-step-drum-sequencer
# Based on code by Tod Kurt @todbot https://github.com/todbot/picostepseq

# Uses General MIDI drum notes on channel 10
# Range is note 35/B0 - 81/A4, but classic 808 set is defined here

import stepper
import microcontroller
import drum_set
import ticker
import hardware
import relative_encoder
import file_header

class sequencer:
    def refresh_step_led(self, drum_index: int, step: int, state: bool):
        remap = [4, 5, 6, 7, 0, 1, 2, 3]
        new_drum = 4 - drum_index
        new_step = remap[step]
        self.hardware.leds[new_drum * self.stepper.num_steps + new_step] = state
        if state:
            print(f'drum{drum_index} step{step}: on')
        else:
            print(f'drum{drum_index} step{step}: off')

    def refresh_bpm_display(self) -> None:
        self.hardware.display.fill(0)
        self.hardware.display.print(self.ticker.bpm)
        self.hardware.display.show()

    def get_save_length(self) -> int:
        length = file_header.file_header.size
        length += self.drums.get_save_length()
        return length

    def save_state_to_nvm(self) -> None:
        length = self.get_save_length()
        bytes = bytearray(length)
        self.save_state_to_bytes(bytes)
        # in one update, write the saved bytes
        # to nonvolatile memory
        microcontroller.nvm[0:length] = bytes

    def save_state_to_bytes(self, bytes, offset: int = 0) -> int:
        """
        Stores the state of the sequencer in a bytearray; if
        the offset parameter is given, uses that as an offset
        to store the state.
        """
        index = offset
        header = file_header.file_header(
            len(self.drums),
            self.stepper.num_steps,
            self.ticker.bpm)
        index += header.save_state_to_bytes(bytes, index)
        index += self.drums.save_state_to_bytes(bytes, index)
        return index - offset

    def load_state_from_nvm(self) -> None:
        length = self.get_save_length()
        bytes = microcontroller.nvm[0:length]
        self.load_state_from_bytes(bytes)
    
    def load_state_from_bytes(self, bytes, offset: int = 0) -> int:
        """
        Retrieves the state of the sequencer from a bytearray; if
        the offset parameter is given, uses that as an offset
        to read the state.
        """
        index = offset
        header = file_header.file_header(
            len(self.drums),
            self.stepper.num_steps,
            self.ticker.bpm)
        index += header.load_state_from_bytes(bytes, index)
        index += self.drums.load_state_from_bytes()
        self.ticker.set_bpm(header.bpm)
        return index - offset

    def __init__(self, bpm) -> None:
        num_steps = 8  # number of steps/switches per row
        self.hardware = hardware.hardware()
        self.ticker = ticker.ticker(bpm)
        self.stepper = stepper.stepper(num_steps)
        self.drums = drum_set.drum_set(self.hardware.midi, num_steps)
        self.tempo_encoder = relative_encoder.relative_encoder(self.hardware.tempo_encoder)
        self.step_shift_encoder = relative_encoder.relative_encoder(self.hardware.step_shift_encoder)
        self.pattern_length_encoder = relative_encoder.relative_encoder(self.hardware.pattern_length_encoder)

    def setup(self) -> None:
        self.hardware.leds.write_config(0)
        self.hardware.display.brightness = 0.3

        # default starting sequence
        self.drums.add_drum(drum.BassDrum)
        self.drums.add_drum(drum.AcousticSnare)
        self.drums.add_drum(drum.LowFloorTom)
        self.drums.add_drum(drum.PedalHiHat)
        self.drums.add_drum(drum.CowBell)

        # try to load the state (no-op if NVM not valid)
        try:
            self.load_state_from_nvm()
        # TODO: This should be a specific exception
        except ValueError:
            pass

        self.refresh_bpm_display()

        # light up initial LEDs
        for drum_index in range(len(self.drums)):
            drum = self.drums[drum_index]
            for step_index in range(self.stepper.num_steps):
                self.refresh_step_led(drum_index, step_index, drum.sequence[step_index])
        self.hardware.leds.write()

    def run_main_loop(self) -> None:
        self.hardware.start_button.update()
        if self.hardware.start_button.fell:  # pushed encoder button plays/stops transport
            # Toggle playing state
            self.ticker.toggle_playing()

            if not self.ticker.playing:
                self.drums.print_sequence()
                self.save_state_to_nvm()
            self.stepper.reset()
            print("*** Play:", self.ticker.playing)

        self.hardware.reverse_button.update()
        if self.hardware.reverse_button.fell:
            self.stepper.reverse()

        # switches add or remove steps
        switch = self.hardware.switches.events.get()
        if switch:
            if switch.pressed:
                i = switch.key_number
                print(f"key pressed: {i}")
                drum_index = i // self.stepper.num_steps
                step_index = i % self.stepper.num_steps
                drum = self.drums[drum_index]
                drum.sequence.toggle(step_index) # toggle step
                self.refresh_step_led(drum_index, step_index, drum.sequence[step_index])  # toggle light
                self.hardware.leds.write()

        # TODO: I don't understand why we only want to check the encoder between steps
        check_encoder = not self.ticker.playing

        if self.ticker.playing:
            if self.ticker.advance():
                # TODO: how to display the current step? Separate LED?
                self.drums.play_step(self.stepper.current_step)
                self.stepper.advance_step()
                check_encoder = True

        if check_encoder:
            tempo_encoder_delta = self.tempo_encoder.read_value()
            if tempo_encoder_delta != 0:
                self.ticker.adjust_bpm(tempo_encoder_delta)
                self.refresh_bpm_display()

            step_shift_encoder_delta = self.step_shift_encoder.read_value()
            if step_shift_encoder_delta != 0:
                self.stepper.adjust_range_start(step_shift_encoder_delta)

            pattern_length_encoder_delta = self.attern_length_encoder.read_value()
            if pattern_length_encoder_delta != 0:
                self.stepper.adjust_range_length(pattern_length_encoder_delta)

sequencer = sequencer(bpm=120)
sequencer.setup()
while True:
    sequencer.run_main_loop()

# suppresions:
# type: ignore
