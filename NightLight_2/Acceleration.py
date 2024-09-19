from machine import I2C, Pin
import struct

class Acceleration():
    def __init__(self, scl, sda, addr = 0x62):
        self.addr = addr
        self.i2c = I2C(1,scl=scl, sda=sda, freq=100000) 
        self.connected = False
        if self.is_connected():
            print('connected')
            self.write_byte(0x11,0) #start data stream

    def is_connected(self):
        options = self.i2c.scan() 
        print(options)
        self.connected = self.addr in options
        return self.connected 
            
    def read_accel(self):
        buffer = self.i2c.readfrom_mem(self.addr, 0x02, 6) # read 6 bytes starting at memory address 2
        return struct.unpack('<hhh',buffer)

    def write_byte(self, cmd, value):
        self.i2c.writeto_mem(self.addr, cmd, value.to_bytes(1,'little'))

scl = Pin('GPIO27', Pin.OUT)
sda = Pin('GPIO26', Pin.OUT)

t = Acceleration(scl, sda)
print(t.read_accel())