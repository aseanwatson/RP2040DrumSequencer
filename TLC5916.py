import digitalio
import time

class TLC5916:
    def index_mask(i):
        return (i // 8, 1 << (i % 8))

    def get_digital_out(pin):
        pin = digitalio.DigitalInOut(pin)
        pin.direction = digitalio.Direction.OUTPUT
        return pin

    def __init__(self, clk_pin, le_pin, sdi_pin, oe_pin, n):
        self.ba = bytearray(n)
        self.clk = TLC5916.get_digital_out(clk_pin)
        self.le = TLC5916.get_digital_out(le_pin)
        self.sdi = TLC5916.get_digital_out(sdi_pin)
        self.oe = TLC5916.get_digital_out(oe_pin)
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

    def pulse_clock(self):
        self.clk.value = True
        time.sleep(0.00001)
        self.clk.value = False

    def write_byte(self, byte):
        for i in range(8):
            self.sdi.value = bool(byte & (1 << i))
            self.pulse_clock()

    def write(self):
        for byte in self.ba:
            self.write_byte(byte)
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
            self.pulse_clock()
        self.oe.value  = False

    def write_config(self, value):
        self.set_special_mode(True)
        for j in range(len(self.ba)):
            self.write_byte(value)
        self.pulse_latch()
        self.set_special_mode(False)
