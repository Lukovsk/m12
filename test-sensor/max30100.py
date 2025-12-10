MAX30100_DEVICE_ID = 0x57
REG_MODE_CONFIG = 0x06
REG_LED_CONFIG = 0x09
REG_TEMP_INT = 0x16
REG_TEMP_FRAC = 0x17
REG_FIFO_DATA = 0x05


class MAX30100:
    def __init__(self, i2c=None):
        self.i2c = i2c
        self.addr = MAX30100_DEVICE_ID

        try:
            self.i2c.readfrom(self.addr, 1)
        except OSError:
            print("Not found MAX30100!")
            return

        self.set_mode(0x03)
        self.set_led_current(0x07)
        self.set_led_width(0x03)
        self.set_sampling_rate(0x01)

    def _write_reg(self, reg, value):
        self.i2c.writeto(self.addr, bytes([reg, value]))

    def _read_reg(self, reg, nbytes=1):
        self.i2c.writeto(self.addr, bytes([reg]))
        return self.i2c.readfrom(self.addr, nbytes)

    def set_mode(self, mode):
        self._write_reg(REG_MODE_CONFIG, mode)

    def set_led_current(self, current):
        self._write_reg(REG_LED_CONFIG, current)

    def set_led_width(self, width):
        pass

    def set_sampling_rate(self, rate):
        pass

    def read_sensor(self):
        data = self._read_reg(REG_FIFO_DATA, 4)
        ir = (data[0] << 8) | data[1]
        red = (data[2] << 8) | data[3]
        return ir, red
