import machine, time, neopixel, asyncio, network
from machine import Pin, PWM

from mqtt import MQTTClient

class Nightlight:
    #Initializing Class
    def __init__(self):

        # mqtt initialization of client and subscribing to topic 'JaylenRoberto'
        mqtt_broker = 'broker.hivemq.com'
        port = 1883
        topic_sub = 'ME35-24/JaylenRoberto'
        self.client = MQTTClient('ME35_chris', mqtt_broker , port, keepalive=60)
        self.client.connect()
        print('Connected to %s MQTT broker' % (mqtt_broker))
        self.client.set_callback(self.callback)          # set the callback if anything is read
        self.client.subscribe(topic_sub.encode())   # subscribe to a bunch of topics

        #Maximum amount in 16 bit
        self.max_bit = 65535


        # Define flags for controlling button press and mqtt messages
        self.flag = False
        self.mqtt_flag = False

        #Pico board initializations: neopixel, led, buzzer
        self.neo = neopixel.NeoPixel(Pin(28),1)
        self.button = Pin('GPIO20', Pin.IN, Pin.PULL_UP)
        self.blue_led = PWM(Pin(0, Pin.OUT))
        self.blue_led.freq(100)
        self.buzzer = PWM(Pin('GPIO18', Pin.OUT))
        self.buzzer.freq(440)



    #prints the recieved message from mqtt
    def callback(self, topic, msg):
        print((topic.decode(), msg.decode()))


    #Breathing definition which has the blue light breathe continously
    async def breathing(self):
        while not self.mqtt_flag:
            #makes the blue led "breath" continously
            for i in range(0,self.max_bit,500):
                    self.blue_led.duty_u16(i)
                    await asyncio.sleep(0.01)

    # Controls the buzzer and neopixel based on a button press.
    # This button press will make the buzzer beep a tune, but also change
    # the neopixel color in a pattern, based on the state of the button (flag)
    async def buzzer_cycle(self):
        #set base neopixel color
        self.neo[0] = (255, 0, 0)
        self.neo.write()
        while not self.mqtt_flag:
            #checks if button has been pressed
            if self.flag:
                #call function button_routine
                routine = asyncio.create_task(self.button_routine())
                await routine

                #resets button
                self.flag = False
            else:
                self.buzzer.duty_u16(0)
            await asyncio.sleep(1)  # Check flag status every 1 second

    #Called by button_cycle, isolates the routine to its own function for code cleanliness
    async def button_routine(self):
        sleep_time = 0.3

        self.neo[0] = (255, 165, 0)
        self.neo.write()
        self.buzzer.freq(262)
        self.buzzer.duty_u16(32768)
        await asyncio.sleep(sleep_time)

        self.neo[0] = (255, 255, 0)
        self.neo.write()
        self.buzzer.freq(294)
        await asyncio.sleep(sleep_time)

        self.neo[0] = (0, 255, 0)
        self.neo.write()
        self.buzzer.freq(330)
        await asyncio.sleep(sleep_time)

        self.neo[0] = (0, 0, 255)
        self.neo.write()
        self.buzzer.freq(349)
        await asyncio.sleep(sleep_time)

        self.neo[0] = (75, 0, 130)
        self.neo.write()
        self.buzzer.freq(330)
        await asyncio.sleep(sleep_time)

        self.neo[0] = (238, 130, 238)
        self.neo.write()
        self.buzzer.freq(294)
        await asyncio.sleep(sleep_time)

        self.neo[0] = (255, 0, 0)
        self.neo.write()
        self.buzzer.freq(262)
        await asyncio.sleep(sleep_time)

        #end routine
        self.buzzer.duty_u16(0)
        self.neo[0] = (255, 0, 0)
        self.neo.write()

    #Toggles flag to initiate buzzer and neopixel routine when the button has been pressed
    async def toggle_flag(self):
        prev_state = self.button.value()  # Initial state
        while not self.mqtt_flag:
            current_state = self.button.value()
            if prev_state == 1 and current_state == 0:  # Button pressed (falling edge)
                self.flag = True
            prev_state = current_state
            await asyncio.sleep(0.1)

    #toggles the mqtt flag on a message recieved from the topic 'JaylenRoberto'
    async def toggle_mqtt(self):
        # global mqtt_flag
        self.mqtt_flag = False
        while not self.mqtt_flag:
            #x is None when no message has been received, and is filled otherwise
            x = self.client.check_msg()

            #checking for a message to have been received
            if x == None:
                #no message
                self.mqtt_flag = False
            else:
                #message
                print('message received')
                self.mqtt_flag = True
            await asyncio.sleep(1)


    # Sets all variables to zero "shutting" everything down when
    # second mqtt message is recieved
    async def shutdown(self):
        print('shutting down')
        self.buzzer.duty_u16(0)
        self.neo[0] = (0, 0, 0)
        self.neo.write()
        self.blue_led.duty_u16(0)

    #the main coroutine
    async def main(self):
        starter = asyncio.create_task(self.toggle_mqtt())
        await starter
        # Create and schedule tasks
        task4 = asyncio.create_task(self.toggle_mqtt())
        await asyncio.sleep(0.01)
        task1 = asyncio.create_task(self.breathing())
        task2 = asyncio.create_task(self.buzzer_cycle())
        task3 = asyncio.create_task(self.toggle_flag())
        # Wait for all tasks to complete (they run indefinitely in this case)
        await asyncio.gather(task1, task2, task3, task4)
        stopper = asyncio.create_task(self.shutdown())
        await stopper

#Connecting to network Tufts_Robot
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Tufts_Robot', '')

while wlan.ifconfig()[0] == '0.0.0.0':
    print('.', end=' ')
    time.sleep(1)

print(wlan.ifconfig())

# Running class
f = Nightlight()
asyncio.run(f.main())
