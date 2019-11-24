# Code sourced from:
# https://github.com/seanbechhofer/raspberrypi/blob/master/python/TSL2561.py
# https://github.com/adafruit/Adafruit_CircuitPython_TSL2561/blob/0c205ed557cf03bad6ab73f10a4b132b40d47bd6/adafruit_tsl2561.py#L127
import time
import smbus

_DEFAULT_ADDRESS     = 0x39
_COMMAND_BIT         = 0x80

_CONTROL_POWERON     = 0x03
_CONTROL_POWEROFF    = 0x00

_REGISTER_CONTROL    = 0x00
_REGISTER_TIMING     = 0x01
_REGISTER_CHAN0_LOW  = 0x0C
_REGISTER_CHAN1_LOW  = 0x0E
_GAIN_SCALE = (16, 1)
_TIME_SCALE = (0.034, 0.252, 1)
_CLIP_THRESHOLD = (4900, 37000, 65000)

class TSL2561:

    def __init__(self, bus, address = _DEFAULT_ADDRESS, pause = 1):
        self.bus = bus
        self.address = address
        self.pause = pause
        self.gain = 0
        self.integration_time = 2
        self.enable()                # power on
        self.set_gain()              # 1x gain preselected
        self.set_integration_time()  # 402ms integration
        
    def enable(self):
        self.bus.write_byte_data(self.address, _COMMAND_BIT | _REGISTER_CONTROL, _CONTROL_POWERON)
        
    def disable(self):
        self.bus.write_byte_data(self.address, _COMMAND_BIT | _REGISTER_CONTROL, _CONTROL_POWEROFF)

    def set_gain(self, gain = 0):
        #       0x00(00)    gain = 1x
        #       0x10(00)    gain = 16x
        if (gain != self.gain):
            self.bus.write_byte_data(self.address, _COMMAND_BIT | _REGISTER_TIMING, gain<<4 | self.integration_time)
            self.gain = gain                    
            time.sleep(self.pause)
    
    def set_integration_time(self, integration_time = 2):
        #       0x00(00)    integration time = 13.7ms
        #       0x01(01)    integration time = 101ms
        #       0x02(02)    integration time = 402ms
        if (integration_time != self.integration_time):
            self.bus.write_byte_data(self.address, _COMMAND_BIT | _REGISTER_TIMING, self.gain<<4 | integration_time)
            self.integration_time = integration_time
            time.sleep(self.pause)
            
    def read_broadband(self):
        low, high = self.bus.read_i2c_block_data(self.address, _COMMAND_BIT | _REGISTER_CHAN0_LOW, 0x02)
        return high << 8 | low

    def read_infrared(self):
        low, high = self.bus.read_i2c_block_data(self.address, _COMMAND_BIT | _REGISTER_CHAN1_LOW, 0x02)
        return high << 8 | low

    def read_lux(self):
        ch0, ch1 = self.read_broadband(), self.read_infrared()
        if ch0 == 0:
            return None
        if ch0 > _CLIP_THRESHOLD[self.integration_time]:
            return None
        if ch1 > _CLIP_THRESHOLD[self.integration_time]:
            return None
        ratio = ch1 / ch0
        if ratio >= 0 and ratio <= 0.50:
            lux = 0.0304 * ch0 - 0.062 * ch0 * ratio**1.4
        elif ratio <= 0.61:
            lux = 0.0224 * ch0 - 0.031 * ch1
        elif ratio <= 0.80:
            lux = 0.0128 * ch0 - 0.0153 * ch1
        elif ratio <= 1.30:
            lux = 0.00146 * ch0 - 0.00112 * ch1
        else:
            lux = 0.
        # Pretty sure the floating point math formula on pg. 23 of datasheet
        # is based on 16x gain and 402ms integration time. Need to scale
        # result for other settings.
        # Scale for gain.
        lux *= _GAIN_SCALE[self.gain]
        # Scale for integration time.
        lux /= _TIME_SCALE[self.integration_time]
        return lux                        

if __name__ == "__main__":
    bus = smbus.SMBus(1)
    tsl=TSL2561(bus)
    tsl.set_gain(0)
    tsl.set_integration_time(0)
    test = tsl.read_lux()
    print(test)
    
'''
import smbus
import time

# Get I2C bus
bus = smbus.SMBus(1)

tsl2561Address = 0x39 # TSL2561 address, (57)
# Select control register, 0x00(00) with command register, 0x80(128)
#       0x03(03)    Power ON mode
bus.write_byte_data(0x39, 0x00 | 0x80, 0x03)
# TSL2561 address, 0x39(57)
# Select timing register, 0x01(01) with command register, 0x80(128)
#       0x02(02)    Nominal integration time = 402ms
bus.write_byte_data(0x39, 0x01 | 0x80, 0x02)

time.sleep(0.5)

# Read data back from 0x0C(12) with command register, 0x80(128), 2 bytes
# ch0 LSB, ch0 MSB
data = bus.read_i2c_block_data(0x39, 0x0C | 0x80, 0x02)

# Read data back from 0x0E(14) with command register, 0x80(128), 2 bytes
# ch1 LSB, ch1 MSB
data1 = bus.read_i2c_block_data(0x39, 0x0E | 0x80, 0x02)

# Convert the data
print(data[0],data[1])
ch0 = data[1] * 256 + data[0]
ch1 = data1[1] * 256 + data1[0]

# Output data to screen
print ('Full Spectrum(IR + Visible) :{:.1f} lux'.format(ch0))
print ('Infrared Value :{:.1f} lux'.format(ch1))
print ('Visible Value :{:.1f} lux'.format(ch0 - ch1))
'''