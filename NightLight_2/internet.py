import network
import time
from mqtt import MQTTClient

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
topic_sub = 'ME35-24/#'       # this reads anything sent to ME35
topic_pub = 'ME35-24/tell'


def callback(topic, msg):
    print((topic.decode(), msg.decode()))

client = MQTTClient('ME35_cory', mqtt_broker , port, keepalive=60)
client.connect()
print('Connected to %s MQTT broker' % (mqtt_broker))
client.set_callback(callback)          # set the callback if anything is read
client.subscribe(topic_sub.encode())   # subscribe to a bunch of topics

msg = 'working...'
i = 0
while True:
    i+=1
    if i %5 == 0:
        print('publishing')
        client.publish(topic_pub.encode(),msg.encode())
    client.check_msg()
    time.sleep(1)