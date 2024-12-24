import time
from mqtt import MQTTClient
import network
from machine import Pin, SoftI2C, PWM, ADC
import adxl345

i2c = SoftI2C(scl = Pin(7), sda = Pin(6))
adx = adxl345.ADXL345(i2c)


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Tufts_Robot', '')

while wlan.ifconfig()[0] == '0.0.0.0':
    print('.', end=' ')
    time.sleep(1)

# We should have a valid IP now via DHCP
print(wlan.ifconfig())

mqtt_broker = 'broker.hivemq.com' 
port = 1883
topic_sub = 'ME35-24/Roberto'      
topic_pub = 'ME35-24/Roberto'


def callback(topic, msg):
    print((topic.decode(), msg.decode()))

client = MQTTClient('RobDahalBoard', mqtt_broker , port, keepalive=60)
client.connect()
print('Connected to %s MQTT broker' % (mqtt_broker))
client.set_callback(callback)          # set the callback if anything is read
client.subscribe(topic_sub.encode())   # subscribe to a bunch of topics
# time.sleep(5)
# msg = 'Start'
# client.publish(topic_pub.encode(),msg.encode())


while True:
    yVal = adx.yValue
    #Note interval is sent 100 times larger than used, avoiding decimals
    noteInterval = 45
    if adx.yValue > 20:
        noteInterval = ((1-.45)/(260-20)*(yVal)+97/240)*100
        if noteInterval > 100:
            noteInterval = 100
    elif adx.yValue < -10:
        noteInterval = ((.45-.05)/(-10+220)*(yVal)+197/420)*100
        if noteInterval < 5:
            noteInterval = 5
    
    #Debugging
    ans = noteInterval/100
    print('y = ' + str(yVal) + ' time = ' + str(ans))
    
    #Message send
    temp = int(noteInterval)
    msg = str(temp)
    print(msg)
    client.publish(topic_pub.encode(),msg.encode())
    time.sleep(.4)
