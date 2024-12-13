import usb_midi
from bitarray import bitarray

class drum:
    def __init__(self, name: str, note: int, sequence: bitarray):
        self.name = name
        self.note = note
        self.sequence = sequence

    def __repr__(self) -> str:
        return f'drum({repr(self.name)},{repr(self.note)},{repr(self.sequence)})'

    def play(self, midi: usb_midi.PortOut, step: int) -> None:
        if self.sequence[step]:
            midi_msg_on = bytearray([0x99, self.note, 120])  # 0x90 is noteon ch 1, 0x99 is noteon ch 10
            midi_msg_off = bytearray([0x89, self.note, 0])
            midi.write(midi_msg_on)
            midi.write(midi_msg_off)

