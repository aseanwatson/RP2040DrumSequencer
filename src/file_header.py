import struct
class file_header:
    """format of the header in NVM for save_state/load_state:
        < -- little-endian; lower bits are more significant
        B -- magic number
        B -- number of drums (unsigned byte: 0 - 255)
        B -- number of steps (unsigned byte: 0 - 255)
        H -- BPM beats per minute (unsigned short: 0 - 65536)"""
    format = b'<BBBH'
    """magic_number should change if load/save logic changes in and incompatible way"""
    magic_number = 0x02
    size = struct.calcsize(format)
    def __init__(self, drum_count: int, step_count: int, bpm: int) -> None:
        self.magic_number = file_header.magic_number
        self.drum_count = drum_count
        self.step_count = step_count
        self.bpm = bpm

    def get_save_length(self) -> int:
        return file_header.size

    def load_state_from_bytes(self, bytes: bytearray, offset: int = 0) -> int:
        index = offset
        values = struct.unpack_from(file_header.format, buffer = bytes, offset = index)
        index += file_header.size
        # TODO: This should be a more specific exception
        if self.magic_number != values[0]:
            raise ValueError("bad magic number")
        if self.drum_count != values[1]:
            raise ValueError("bad drum_count")
        if self.step_count != values[2]:
            raise ValueError("bad step_count")
        self.bpm = values[3]
        return index - offset

    def save_state_to_bytes(self, bytes: bytearray, offset: int = 0) -> int:
        index = offset
        struct.pack_into(
            file_header.format,
            bytes,
            index,
            file_header.magic_number,
            self.drum_count,
            self.step_count,
            self.bpm)
        index += file_header.size
        return index - offset

