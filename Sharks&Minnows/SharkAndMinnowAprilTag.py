# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# MQTT Example.
# This example shows how to use the MQTT library to publish to a topic.
################################################################################
#Malia Brandt and Roberto Garcia 
#For the Shark and Minnow ME35 Project September 2024
#This is an edited version of provided code from OpenMV on sending mqtt messages.
#This code detects April Tags, sending MQTT messages based on which April Tag is seen. 
#It can send forward, backwards, left, right, and buzzing messages for the robot to
#receive. This code run on OpenMV (the camera).
import time
import network
from mqtt import MQTTClient
import sensor
import math
##################################MQTT SETUP##################################
SSID = "Tufts_Robot"  # Network SSID
KEY = ""  # Network key
# Init wlan module and connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)
while not wlan.isconnected():
    print('Trying to connect to "{:s}"...'.format(SSID))
    time.sleep_ms(1000)
# We should have a valid IP now via DHCP
print("WiFi Connected ", wlan.ifconfig())
client = MQTTClient('ME35_malia90', 'broker.hivemq.com' , 1883, keepalive=60)
client.connect()
###############################april tag setup##################################
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # must turn this off to prevent image washout...
sensor.set_auto_whitebal(False)  # must turn this off to prevent image washout...
clock = time.clock()
def check_tag():
    clock.tick()
    img = sensor.snapshot()
    for tag in img.find_apriltags():
        img.draw_rectangle(tag.rect, color=(255, 0, 0))
        img.draw_cross(tag.cx, tag.cy, color=(0, 255, 0))
        print_args = (tag.name, tag.id, (180 * tag.rotation) / math.pi)
        print("Tag Family %s, Tag ID %d, rotation %f (degrees)" % print_args)
        return tag.id
    print(clock.fps())
while True:
    tag_id = check_tag()
    #if april tag 0 -- forward
    if tag_id == 0:
        client.publish("ME35-24/Malia", "forward")
    #if april tag 1 -- left
    elif tag_id == 1:
        client.publish("ME35-24/Malia", "left")
    #if april tag 2 -- right
    elif tag_id == 2:
        client.publish("ME35-24/Malia", "right")
    elif tag_id == 3:
        client.publish("ME35-24/Malia", "back")
    elif tag_id == 4:
        client.publish("ME35-24/Malia", "buzz")
    time.sleep_ms(1000)
