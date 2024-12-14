from drum import drum, drum_definition
import usb_midi
from bitarray import bitarray

class drum_set:
    def __init__(self, midi: usb_midi.PortOut, step_count: int):
        self.drums = []
        self.midi = midi
        self.step_count = step_count
    
    def add_custom_drum(self, name: str, note: int) -> None:
        self.drums.append(drum(name, note, bitarray(self.step_count)))

    def add_drum(self, definition: drum_definition) -> None:
        self.add_custom_drum(name=definition.short_name, note=definition.note)

    def print_sequence(self) -> None:
        print("drums = [")
        for drum in self.drums:
            print(" " + repr(drum) + ",")
        print("]")

    def play_step(self, step) -> None:
        for drum in self.drums:
            drum.play(self.midi, step)

    def __len__(self) -> int:
        return len(self.drums)

    def __getitem__(self, i: int) -> drum:
        return self.drums[i]

    def __iter__(self):
        return iter(self.drums)


