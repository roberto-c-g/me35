import time
import network
from machine import Pin, PWM

class Motor():

    # Initializer takes pins for the neopixel and buzzer
    def __init__(self, pin1, pin2, pwm, name):
        self.forward = pin1 #Should be PWM
        self.back = pin2 #Should be PWM
        self.pwm = pwm
        self.name = name
        print('motor instantiated, name: '+self.name)
        self.pwmVal = 0
        self.pwm.freq(200)
    
    def goForward(self, val):        
        print(self.name + ' moving forward')
        self.back.off()
        time.sleep(0.01)
        self.forward.on()
        if val < 10000:
            val = 10000
        self.pwmVal = val
        self.pwm.duty_u16(val)
    
    def goBackward(self, val):
        print(self.name + ' moving backward')
        self.forward.off()
        time.sleep(0.01)
        self.back.on()
        if val < 10000:
            val = 10000
        self.pwmVal = val
        self.pwm.duty_u16(val) # where val is a %
    
    def turn(self,val): #initialize a turn about wheel side by decreasing speeds
        print(self.name + ' turning')
        self.back.off()
        time.sleep(0.01)
        self.forward.on()
        decrease = val/65535 * 1000 # will increment by up to 1000
        if(self.pwmVal-decrease > 1000):
            self.pwmVal = int(self.pwmVal - decrease)
        self.pwm.duty_u16(self.pwmVal)

    def stop(self):
        print(self.name + ' stopping ')
        self.forward.off()
        self.back.off()
    
    def getPWM(self):
        return self.pwmVal
    
    def test(self):
        for i in range(25,101):
            self.goForward(int(float(i)/100*65355))
            print(i)
            time.sleep(0.05)
        for i in range(25, 101):
            self.goBackward(int(float(i)/100*65355))
            time.sleep(0.05)
        self.stop()
