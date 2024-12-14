from drum import drum, drum_definition
import usb_midi
from bitarray import bitarray

class drum_set:
    """drum_set class: a list of drum objects"""
    def __init__(self, midi: usb_midi.PortOut, step_count: int):
        self.drums = []
        self.midi = midi
        self.step_count = step_count
    
    def add_custom_drum(self, name: str, note: int) -> None:
        """add_custom_drum(name, note): directly add a drum without a drum_definition."""
        self.drums.append(drum(name, note, bitarray(self.step_count)))

    def add_drum(self, definition: drum_definition) -> None:
        """add_drum(definition): add a drum based on a drum_definition."""
        self.add_custom_drum(name=definition.short_name, note=definition.note)

    def print_sequence(self) -> None:
        """print_sequence(): output the drum sequence."""
        print("drums = [")
        for drum in self.drums:
            print(" " + repr(drum) + ",")
        print("]")

    def play_step(self, step) -> None:
        """play_step(): plays a given step on all drums (if their sequence says to)."""
        for drum in self.drums:
            drum.play(self.midi, step)

    def __len__(self) -> int:
        """__len__(): lets the len(...) funtion work on a drum_set; gives number of drums."""
        return len(self.drums)

    def __getitem__(self, i: int) -> drum:
        """__getitem__(i): lets drums[i] work; gets a drum in the set, like a list."""
        return self.drums[i]

    def __iter__(self):
        """__iter__(): lets the for keywork work on a drum_set, gets each drum in the set."""
        return iter(self.drums)