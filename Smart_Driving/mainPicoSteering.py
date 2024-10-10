import time
import network
from machine import Pin, PWM
from mqtt import MQTTClient
from Motor import Motor #wrote a class for motor objects
import uasyncio as asyncio
# ---- AprilTag-following car objetives----
# Will read in a pwm from the aprilTag
# all processing happens in aprilTag
# all forward/backwards movement, no steering
# will read a negative pwm as going backwards
# ---- MQTT THINGS ----
#ssid = 'Tufts_Robot'
#password = ''
ssid = 'Tufts_Robot'
password = ''
mqtt_broker = 'broker.hivemq.com'
port = 1883
topic_sub = 'ME35-24/potato'
isOn = False
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        time.sleep(1)
    print('connected to wifi')
def connect_mqtt(client):
    client.set_callback(callback)
    client.connect()
    client.subscribe(topic_sub.encode())
    print(f'Subscribed to {topic_sub}')
def callback(topic, msg):
    val = msg.decode()
    print((topic.decode(), val))
    pwm = int(val[3:])
    steer = int(val[1]) * 5000
    lSteer = 0
    rSteer = 0
    if val[0] == 'R':
        lSteer = -1*steer
        rSteer = steer
    else:
        rSteer = -1*steer
        lSteer = steer
    if val[2] == 'F':
        rightMotor.goForward(pwm + rSteer)
        leftMotor.goForward(pwm + lSteer)
    elif val[2] == 'B':
        rightMotor.goBackward(pwm + lSteer)
        leftMotor.goBackward(pwm + rSteer)
    else:
        rightMotor.stop()
        leftMotor.stop()
async def mqtt_handler(client):
    while True:
        try:
            client.check_msg()
            await asyncio.sleep(0.01)
        except Exception as e:
            print('MQTT callback failed')
            connect_mqtt(client)
# --- Defining pins and motor objects ----
# NOTE: PINS 1-3 MAY BE FRIED ON ANNE'S PICO...
motor1A = Pin('GPIO7', Pin.OUT)
motor1B = Pin('GPIO8', Pin.OUT)
motor1PWM = PWM(Pin('GPIO9', Pin.OUT))
rightMotor = Motor(motor1A, motor1B, motor1PWM, 'left')
motor2A = Pin('GPIO4',Pin.OUT)
motor2B = Pin('GPIO5', Pin.OUT)
motor2PWM = PWM(Pin('GPIO6',Pin.OUT))
leftMotor = Motor(motor2A, motor2B, motor2PWM, 'right')
connect_wifi()
client = MQTTClient('ME35_chris', mqtt_broker, port, keepalive=60)
client.set_callback(callback)
client.connect()
client.subscribe(topic_sub.encode())
print(f'Subscribed to {topic_sub}')
asyncio.run(mqtt_handler(client))
connect_wifi()
client = MQTTClient('ME35_annePico', mqtt_broker, port, keepalive=60)
connect_mqtt(client)
asyncio.run(mqtt_handler(client))
