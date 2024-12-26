import usb_midi
from . import drum
from . import bitarray

class drum_set:
    """drum_set class: a list of drum objects"""
    def __init__(self, midi: usb_midi.PortOut, step_count: int):
        self.drums = []
        self.midi = midi
        self.step_count = step_count
    
    def add_custom_drum(self, name: str, note: int) -> None:
        """add_custom_drum(name, note): directly add a drum without a drum_definition."""
        self.drums.append(drum.drum(name, note, bitarray.bitarray(self.step_count)))

    def add_drum(self, definition: drum.drum_definition) -> None:
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
    
    def get_step_value(self, drum_index: int, step_index: int) -> bool:
        """get the step value of a drum"""
        return self[drum_index].sequence[step_index]

    def __len__(self) -> int:
        """__len__(): lets the len(...) funtion work on a drum_set; gives number of drums."""
        return len(self.drums)

    def __getitem__(self, i: int) -> drum.drum:
        """__getitem__(i): lets drums[i] work; gets a drum in the set, like a list."""
        return self.drums[i]

    def __iter__(self):
        """__iter__(): lets the for keywork work on a drum_set, gets each drum in the set."""
        return iter(self.drums)

    def get_save_length(self) -> int:
        length = 0
        for drum in self.drums:
            length += drum.get_save_length()
        return length

    def save_state_to_bytes(self, bytes, offset: int = 0) -> int:
        """
        Stores the state of the drum_set in a bytearray; if
        the offset parameter is given, uses that as an offset
        to store the state.
        """
        index = offset
        for drum in self.drums:
            index += drum.save_state_to_bytes(bytes, index)
        return offset - index

    def load_state_from_bytes(self, bytes, offset: int = 0) -> int:
        """
        Retrieves the state of the drum_set from a bytearray; if
        the offset parameter is given, uses that as an offset
        to read the state.
        """
        index = offset
        for drum in self.drums:
            index += drum.load_state_from_bytes(self, index)
        return offset - index