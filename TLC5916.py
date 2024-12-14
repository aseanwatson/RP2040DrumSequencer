import digitalio
import time

class TLC5916:
    def index_mask(i):
        """index_mask(i): convert a bit index into a byte index and a bitmask"""
        return (i // 8, 1 << (i % 8))

    def get_digital_out(pin):
        """get_digitial_out(pin): helper to get a DigitalInOut in OUTPUT mode"""
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
        """__setitem__(i, b): Sets the i-th LED to on (if b is True) or off (if b is False)"""
        index, mask = TLC5916.index_mask(i)
        if index < len(self.ba):
            if b:
                self.ba[index] |= mask
            else:
                self.ba[index] &= ~mask

    def __getitem__(self, i):
        """__getitem__(i): Tests if the i-th LED is on"""
        index, mask = TLC5916.index_mask(i)
        if index < len(self.ba):
            return self.ba[index] & mask != 0
        return False

    def pulse_latch(self):
        """pulse_latch(): shared code to pusle the LE (latch) pin on/off"""
        self.le.value = True
        time.sleep(0.00001)
        self.le.value = False

    def pulse_clock(self):
        """pulse_clock(): shared code to pusle the CLK (clock) pin on/off"""
        self.clk.value = True
        time.sleep(0.00001)
        self.clk.value = False

    def write_byte(self, byte):
        """write_byte(): shared code to send a byte on the serial data in (SDI) pin, pulsing the CLK (clock) each time
        
        It sends bit 0 first (little endian)."""
        for i in range(8):
            self.sdi.value = bool(byte & (1 << i))
            self.pulse_clock()

    def write(self):
        """write(): updates the output pins to match values set."""
        for byte in self.ba:
            self.write_byte(byte)
        self.pulse_latch()

    def set_special_mode(self, val):
        """set_special_mode(val): Sets the chip into special mode (if val = True) or normal mode (ohterwise)."""
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
        """write_config(value): sets the current configuration to value.
        Value is a byte CM:HC:CC5:CC4:CC3:CC2:CC1:CC0 (CC0 is shifted out first).

        See https://www.ti.com/lit/ds/symlink/tlc5916.pdf section 10.1.4 for details.
        The current is determined by this value and the value of the R_ext resistor.

        For CM = 0; HC = 0:

        I_out = (64+D)/(40.6349206349206 * R_ext)
        where D = CC5 << 0 | CC4 << 1 | CC3 << 2 | CC2 << 3 | CC1 << 4 | CC0 << 5

        If set, HC multiplies the current by a factor of 2.

        CM should be clear for the range 3mA to 40mA; set for 10mA to 120mA.  If set, CM multiplies the current by a factor of 3."""
        self.set_special_mode(True)
        for j in range(len(self.ba)):
            self.write_byte(value)
        self.pulse_latch()
        self.set_special_mode(False)
