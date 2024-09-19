from machine import Pin, PWM
import uasyncio as asyncio
import random
import neopixel
import time

# buttonPin is GPIO20
# blueLEDPin is GPIO1
# buzzerPin is GPIO19

class Nightlight:
    # Initialize GPIO values and enable variables
    def __init__(self, buttonPin, blueLEDPin, buzzerPin):

        self.button = Pin(buttonPin, Pin.IN)
        self.bLED = PWM(Pin(blueLEDPin, Pin.OUT))
        self.bLED.freq(1000)
        self.buzz = PWM(Pin(buzzerPin, Pin.OUT))
        self.buzz.freq(260)
        self.led = neopixel.NeoPixel(Pin(28),1)

        self.enable = False
        self.buzzOn = False
        self.neoOn = False
        self.bump = False
        self.currentColor = [0, 10, 5]

    # Changes the neopixel color based on a randomly selected index
    def changeColor(self):
        prevColor = self.currentColor
        colorList = [[10, 0, 0], [10, 2, 0], [10, 5, 0], 
                     [0, 10, 0], [0, 10, 5], [0, 3, 10],
                     [5, 0, 10], [10, 5, 2], [10, 10, 10]]
        newColor = colorList[random.randint(0, 8)]
        while True:
            if newColor == prevColor:
                newColor = colorList[random.randint(0, 8)]
            else:
                break
        self.currentColor = newColor
    
    # Creates a counter to control the blue LED duty cycle
    async def breathe(self):
        RATE = 1000
        count = 1 # 1 if counting up, 0 if counting down
        i = RATE

        while True:
            if self.enable:
                if i >= 65535:
                    count = 0
                elif i <= 0:
                    count = 1

                if count == 1:
                    i = i + RATE
                elif count == 0:
                    i = i - RATE
            
                self.bLED.duty_u16(i)
            else:
                self.bLED.duty_u16(0)

            await asyncio.sleep(0.01)
    
    # Determines the state of the button
    async def check_button_status(self):
        while True:
            if self.enable:
                self.neoOn = True
                if self.button.value() == 0 or self.bump: # The button is being pressed
                    self.changeColor()
                    self.buzzOn = True
                    await asyncio.sleep(1)
            else: # The buttton is not being pressed
                self.neoOn = False
            await asyncio.sleep(0.01)

    # Handler function for the neopixel based on the neoOn enable
    async def neo(self):
        while True:
            if self.neoOn:
                self.led[0] = self.currentColor
            else:
                self.led[0] = (0, 0, 0)
            self.led.write()
            await asyncio.sleep(0.01)

    # Handler function for the buzzer
    async def buzzer(self):
        while True:
            if self.enable:    
                if self.buzzOn:    
                    # self.buzz.duty_u16(50000)
                    # await asyncio.sleep(0.5)
                    # self.buzz.duty_u16(0)
                    n = [262, 262, 392, 392, 440, 440, 392]
                    # n = [262, 294, 330, 392, 440, 392, 330, 294, 262]
                    for i in n:
                        self.buzz.freq(i)
                        self.buzz.duty_u16(20000)
                        await asyncio.sleep(0.25)
                        self.buzz.duty_u16(0)
                        await asyncio.sleep(0.1)
                        self.buzzOn = False
                else:
                    self.buzz.duty_u16(0)
            await asyncio.sleep(0.01)
