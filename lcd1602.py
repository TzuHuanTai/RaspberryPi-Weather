import smbus
from time import *

# LCD Address
ADDRESS = 0x3F

# commands
LCD_CLEARDISPLAY   = 0b00000001
LCD_RETURNHOME     = 0b00000010
LCD_ENTRYMODESET   = 0b00000100
LCD_DISPLAYCONTROL = 0b00001000
LCD_CURSORSHIFT    = 0b00010000
LCD_FUNCTIONSET    = 0b00100000
LCD_SETCGRAMADDR   = 0b01000000
LCD_SETDDRAMADDR   = 0b10000000

# flags for display entry mode
LCD_ENTRYRIGHT          = 0b00000000
LCD_ENTRYLEFT           = 0b00000010
LCD_ENTRYSHIFTINCREMENT = 0b00000001
LCD_ENTRYSHIFTDECREMENT = 0b00000000

# flags for display on/off control
LCD_DISPLAYON  = 0b00000100
LCD_DISPLAYOFF = 0b00000000
LCD_CURSORON   = 0b00000010
LCD_CURSOROFF  = 0b00000000
LCD_BLINKON    = 0b00000001
LCD_BLINKOFF   = 0b00000000

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0b00001000
LCD_CURSORMOVE  = 0b00000000
LCD_MOVERIGHT   = 0b00000100
LCD_MOVELEFT    = 0b00000000

# flags for function set
LCD_8BITMODE = 0b00010000
LCD_4BITMODE = 0b00000000
LCD_2LINE    = 0b00001000
LCD_1LINE    = 0b00000000
LCD_5x10DOTS = 0b00000100
LCD_5x8DOTS  = 0b00000000

# flags for backlight control
LCD_BACKLIGHT   = 0b00001000
LCD_NOBACKLIGHT = 0b00000000

En = 0b00000100 # Enable bit
Rw = 0b00000010 # Read/Write bit
Rs = 0b00000001 # Register select bit

class LCD:
    #initializes objects and lcd
    def __init__(self, bus, address = ADDRESS):
        self.bus = bus
        self.address = address
        self.backlight = LCD_BACKLIGHT
        self.lcd_write(0b10) # initial
        self.lcd_write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
        self.lcd_write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
        sleep(0.2)
      
    def write_cmd(self, cmd):
        self.bus.write_byte(self.address, cmd)
        sleep(0.0001)

    # clocks EN to latch command
    def lcd_strobe(self, data):
        self.write_cmd(data | En | self.backlight)
        sleep(.0005)
        self.write_cmd(((data & ~En) | self.backlight))
        sleep(.0001)

    def lcd_write_four_bits(self, data):
        # send ~En first with write_cmd() to ensure initial signal
        self.write_cmd(data | self.backlight)
        self.lcd_strobe(data)

    # write a command to lcd
    def lcd_write(self, cmd, mode=0):
        self.lcd_write_four_bits(mode | (cmd & 0xF0))
        self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))
  
    # put string function
    def lcd_display_string(self, string):
        for char in string:
            self.lcd_write(ord(char), Rs)

    # clear lcd and set to home
    def lcd_clear(self):
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_RETURNHOME)

    # define backlight on/off (lcd.backlight(1); off= lcd.backlight(0)
    def set_backlight(self, state): # for state, 1 = on, 0 = off
        if state == 1:
            self.backlight = LCD_BACKLIGHT
        elif state == 0:
            self.backlight = LCD_NOBACKLIGHT
        self.write_cmd(self.backlight)        
    
    def set_cursor(self, row, col):
        '''
        line 1 addr: 0x00~0x0f or 0b0000000~0b0001111 
        line 2 addr: 0x40~0x4f or 0b1000000~0b1001111
        '''
        self.lcd_write((LCD_SETDDRAMADDR | row << 6) | col)
        sleep(0.005)
      
if __name__ == '__main__':
    bus = smbus.SMBus(1)
    mylcd = lcd(bus)
    mylcd.set_cursor(0, 5)
    mylcd.lcd_display_string("test")
    sleep(2) # 2 sec delay
    mylcd.set_backlight(0)
