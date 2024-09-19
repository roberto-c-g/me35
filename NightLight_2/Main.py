from Nightlight import Nightlight
from machine import Pin, PWM, I2C
import uasyncio as asyncio
import network
import time
from mqtt import MQTTClient
from Acceleration import Acceleration
from math import sqrt

enable = False  # Global enable
bump = False
scl = Pin('GPIO27', Pin.OUT)
sda = Pin('GPIO26', Pin.OUT)

# Handles internet connections (must change ssid and password)
def internet():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('Tufts_Robot', '')

    while wlan.ifconfig()[0] == '0.0.0.0':
        print('.', end=' ')
        time.sleep(1)

    # We should have a valid IP now via DHCP
    print(wlan.ifconfig())

# Callback function for MQTT. Sets global enable
def callback(topic, msg):
    global enable
    command = msg.decode()
    print((topic.decode(), msg.decode()))
    if command == 'on':
        enable = True
    if command == 'off':
        enable = False

# MQTT initialization and handler function
async def mqtt():
    mqtt_broker = 'broker.hivemq.com' 
    port = 1883
    topic_sub = 'ME35-24/cory'
    topic_pub = 'ME35-24/Kaisnightlight'

    client = MQTTClient('ME35_cory', mqtt_broker , port, keepalive=60)
    client.connect()
    client.set_callback(callback)          # set the callback if anything is read
    client.subscribe(topic_sub.encode())   # subscribe to a bunch of topics
    
    msg = 'Turn On'
    while True:
        if bump and not enable:
            client.publish(topic_pub.encode(),msg.encode())
            await asyncio.sleep(0)
        client.check_msg()
        await asyncio.sleep(0.25)

async def monitor_accelerometer(t):
    global bump
    mag = 0
    while True:   
        data = t.read_accel()
        newMag = sqrt(data[0]*data[0] + data[1]*data[1] + data[2]*data[2])
        value = newMag - mag
        if abs(value) > 1000 and mag != 0:
            bump = True
            await asyncio.sleep(0.3)
            bump = False
        mag = newMag
        await asyncio.sleep(0.1)

# Creates and runs tasks
async def main():
    global enable
    global scl
    global sda
    global bump
    asyncio.create_task(mqtt())
    nightlight = Nightlight('GPIO20', 'GPIO15', 'GPIO0', 'GPIO19')
    t = Acceleration(scl, sda)
    asyncio.create_task(nightlight.breathe())
    asyncio.create_task(nightlight.check_button_status())
    asyncio.create_task(nightlight.neo())
    asyncio.create_task(nightlight.buzzer())
    asyncio.create_task(monitor_accelerometer(t))
    while True:
        nightlight.enable = enable
        nightlight.bump = bump
        await asyncio.sleep(0.1)

internet()
asyncio.run(main())