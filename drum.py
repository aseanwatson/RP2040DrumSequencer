import usb_midi
from bitarray import bitarray

class drum:
    channel = 10
    velocity = 120
    note_on = 0x90
    note_off = 0x80

    def __init__(self, name: str, note: int, sequence: bitarray):
        self.name = name
        self.note = note
        self.sequence = sequence

    def __repr__(self) -> str:
        return f'drum({repr(self.name)},{repr(self.note)},{repr(self.sequence)})'

    def play(self, midi: usb_midi.PortOut, step: int) -> None:
        if self.sequence[step]:
            channel_flag = drum.channel - 1 # 0 = ch 1, 1 = ch2, ..., 9 = ch 10
            midi_msg_on = bytearray([channel_flag | drum.note_on, self.note, drum.velocity])
            midi_msg_off = bytearray([channel_flag | drum.note_off, self.note, 0])
            midi.write(midi_msg_on)
            midi.write(midi_msg_off)

