import digitalio
import time

class TLC5916:
    def index_mask(i):
        return (i // 8, 1 << (i % 8))

    def __init__(self, clk_pin, le_pin, sdi_pin, oe_pin, n):
        self.ba = bytearray(n)
        self.clk = digitalio.DigitalInOut(clk_pin)
        self.clk.direction = digitalio.Direction.OUTPUT
        self.le = digitalio.DigitalInOut(le_pin)
        self.le.direction = digitalio.Direction.OUTPUT
        self.sdi = digitalio.DigitalInOut(sdi_pin)
        self.sdi.direction = digitalio.Direction.OUTPUT
        self.oe = digitalio.DigitalInOut(oe_pin)
        self.oe.direction = digitalio.Direction.OUTPUT
        self.oe.value = False

    def __setitem__(self, i, b):
        index, mask = TLC5916.index_mask(i)
        if index < len(self.ba):
            if b:
                self.ba[index] |= mask
            else:
                self.ba[index] &= ~mask

    def __getitem__(self, i):
        index, mask = TLC5916.index_mask(i)
        if index < len(self.ba):
            return self.ba[index] & mask != 0
        return False

    def pulse_latch(self):
        self.le.value = True
        time.sleep(0.00001)
        self.le.value = False

    def write(self):
        for i in range(8*len(self.ba)):
            self.sdi.value = self[i]
            self.clk.value = True
            self.clk.value = False
        self.pulse_latch()

    def set_special_mode(self, val):
        # see https://www.ti.com/lit/ds/symlink/tlc5916.pdf
        # section 9.4.1
        pairs = (
            # OE    LE
            (True,  False),
            (False, False),
            (True,  False),
            (True,  val),
            (True,  False),
        )
        for pair in pairs:
            self.oe.value  = pair[0]
            self.le.value  = pair[1]
            self.clk.value = True
            time.sleep(0.00001)
            self.clk.value = False
        self.oe.value  = False

    def write_config(self, value):
        self.set_special_mode(True)
        for j in range(len(self.ba)):
            for i in range(8):
                self.sdi.value = bool(value & (1 << i))
                self.clk.value = True
                self.clk.value = False
        self.pulse_latch()
        self.set_special_mode(False)
