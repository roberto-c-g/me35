from motor import motor
from secrets import WiFi
from mqtt import MQTTClient
from machine import Pin, PWM

#create an instance of motor
#receive mqtt commands
#turn the wheels based on the commands
class receive_motor_info:
    def __init__(self, side):
        #testing leds
        self.led0 = Pin('GPIO0', Pin.OUT)
        self.led1 = Pin('GPIO1', Pin.OUT)
        self.led2 = Pin('GPIO2', Pin.OUT)
        self.led3 = Pin('GPIO3', Pin.OUT)
        self.led4 = Pin('GPIO4', Pin.OUT)
        self.led5 = Pin('GPIO5', Pin.OUT)
        self.led4.off()
        self.led5.off()
        
        #know which side motor we are handling 
        self.side = side
        #connect to tufts wifi
        self.wf = WiFi()
        self.wf.connect_robot()
        
        #initialize mqtt stuff
        self.mqtt_broker = 'broker.hivemq.com' 
        self.port = 1883
        self.topic_sub = 'ME35-24/#'       # this reads anything sent to ME35
        self.topic_pub = 'ME35-24/tell'
        
        #different names for left and right motor
        if self.side == 'left':
            self.client = MQTTClient('ME35_malia_1', self.mqtt_broker , self.port, keepalive=60)
        else:
            self.client = MQTTClient('ME35_malia_2', self.mqtt_broker , self.port, keepalive=60)
        
        self.setup()
        
        #setup motor
        self.me = motor(self.side)
        
        #starting and stopping boolean
        self.start = False
    
        #setup buzzer--starting off
        self.buzzer = PWM(Pin('GPIO18', Pin.OUT))
        self.buzzer.freq(1000)
        self.buzzer.duty_u16(0)
    
    #more setup for mqtt stuff 
    def setup(self):
        self.client.connect()
        print('Connected to %s MQTT broker' % (self.mqtt_broker))
        self.led5.on() #turn led on when connected
        self.client.set_callback(self.callback)          # set the callback if anything is read
        self.client.subscribe(self.topic_sub.encode())   # subscribe to a bunch of topics

    #turn all leds off
    def all_led_off(self):
        self.led0.off()
        self.led1.off()
        self.led2.off()
        self.led3.off()
        self.led4.off()
        
    def callback(self, topic, msg):
        if topic.decode() == 'ME35-24/Malia':
            print('received')
            print(msg.decode())
            #checking for messages from TM to turn whole system on/off
            if msg.decode() == 'on':
                self.start = True
                self.led4.on()
            elif msg.decode() == 'off':
                self.start = False
                self.me.off()
            #once on, check messages for motor commands
            if self.start:
                self.all_led_off()
                if msg.decode() == 'forward':
                    self.me.forward()
                    self.led0.on()
                    self.buzzer.duty_u16(0)
                elif msg.decode() == 'back':
                    self.me.back()
                    self.led1.on()
                    self.buzzer.duty_u16(0)
                elif msg.decode() == 'left':
                    self.me.left()
                    self.led2.on()
                    self.buzzer.duty_u16(0)
                elif msg.decode() == 'right':
                    self.me.right()
                    self.led3.on()
                    self.buzzer.duty_u16(0)
                elif msg.decode() == 'buzz':
                    self.buzzer.duty_u16(5000)
                    

    def main(self):
        while True:
            self.client.check_msg()
