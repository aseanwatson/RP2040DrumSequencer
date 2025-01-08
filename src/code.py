# SPDX-License-Identifier: MIT
# Drum Trigger Sequencer 2040
# This is a modifiaiton of code by John Park (Adafruit Industries). That code is
# MIT Licensed so this will inherit that license.
# see https://learn.adafruit.com/16-step-drum-sequencer/code-the-16-step-drum-sequencer
# Based on code by Tod Kurt @todbot https://github.com/todbot/picostepseq

# Uses General MIDI drum notes on channel 10
# Range is note 35/B0 - 81/A4, but classic 808 set is defined here

from . import sequencer

sequencer = sequencer(bpm=120)
sequencer.setup()
while True:
    sequencer.run_main_loop()

# suppresions:
# type: ignore
