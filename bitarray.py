class bitarray(object):
    """
    A bitarray is logically an array of bool values stored
    as a bytearray
    """

    def __init__(self, data):
        if isinstance(data, int):
            # round up
            bytecount = (data - 1) // 8 + 1
            self._bytes = bytearray(bytecount)
            self._bitscount = data
        else:
            # recursively call __init__
            # to set up something with
            # the right number of
            # bits
            self.__init__(len(data))

            dataiter = iter(data)
            # unroll to decode a byte at
            # a time. When we get to the end of
            # the enumeration, we'll skip the
            # rest with the StopIteration exception
            for byteindex in range(len(self._bytes)):
                byte = 0
                try:
                    if next(dataiter):
                        byte |= 0b0000_0001
                    if next(dataiter):
                        byte |= 0b0000_0010
                    if next(dataiter):
                        byte |= 0b0000_0100
                    if next(dataiter):
                        byte |= 0b0000_1000
                    if next(dataiter):
                        byte |= 0b0001_0000
                    if next(dataiter):
                        byte |= 0b0010_0000
                    if next(dataiter):
                        byte |= 0b0100_0000
                    if next(dataiter):
                        byte |= 0b1000_0000
                except StopIteration:
                    break
                finally:
                    # actaully assign the byte whether
                    # we are breaking out of the loop or
                    # not
                    self._bytes[byteindex] = byte

    def __len__(self) -> int:
        """returns the number of bools in the bitarray"""
        return self._bitscount

    def __repr__(self) -> str:
        """gives code which will create an equivalent bitarray"""
        return f"bitarray(({','.join(['1' if self[i] else '0' for i in range(len(self))])}))"

    def __getindexandmask(self, index):
        """
        helper function to get the index of the byte in
        the bytearray for a given bit. It also gives the
        bitmask to select the bit within that byte
        """
        if index < 0:
            print(f"index={index} too small")
            raise IndexError()
        if index >= self._bitscount:
            print(f"index={index} too big")
            raise IndexError()
        byteindex = index // 8
        bitmask = 1 << (index % 8)
        return (byteindex, bitmask)

    def __getitem__(self, index: int) -> bool:
        """supports the self[index] syntax to read a bit

        Returns True if the bit is set; False otherwise
        """
        byteindex, bitmask = self.__getindexandmask(index)
        return self._bytes[byteindex] & bitmask != 0

    def __setitem__(self, index: int, value: bool) -> None:
        """supports the self[index] syntax to set a bit

        Sets the bit if the value is True; clears it otherwise.
        """
        byteindex, bitmask = self.__getindexandmask(index)
        if value:
            self._bytes[byteindex] |= bitmask
        else:
            self._bytes[byteindex] &= ~bitmask

    def toggle(self, index: int) -> None:
        """toggles the given bit in the array"""
        byteindex, bitmask = self.__getindexandmask(index)
        self._bytes[byteindex] ^= bitmask

    def bytelen(self) -> int:
        """gives the number of bytes needed to store the bitarray"""
        return len(self._bytes)

    def save(self, data: bytearray, start: int = 0) -> None:
        """
        Stores the state of the bitarray in a bytearray; if
        the start parameter is given, uses that as an offset
        to store the state.
        """
        if start + self.bytelen() > len(data):
            raise IndexError()
        data[start : start + self.bytelen()] = self._bytes

    def load(self, data: bytearray, start: int = 0) -> None:
        """
        Retrieves the state of the bitarray from a bytearray; if
        the start parameter is given, uses that as an offset
        to read the state.
        """
        if start + self.bytelen() > len(data):
            raise IndexError()
        self._bytes = data[start : start + self.bytelen()]
