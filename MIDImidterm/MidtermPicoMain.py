import time
from BLE_CEEO import Yell
from mqtt import MQTTClient
import network
from machine import ADC, Pin, PWM
import asyncio

### Internet Setup ###
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# Replace with wifi
wlan.connect('Tufts_Robot', '')
#
while wlan.ifconfig()[0] == '0.0.0.0':
    print('.', end=' ')
    time.sleep(1)
# We should have a valid IP now via DHCP
print(wlan.ifconfig())

mqtt_broker = 'broker.hivemq.com' 
port = 1883
topic_sub = 'ME35-24/Roberto'       # this reads anything sent to ME35
topic_pub = 'ME35-24/Roberto'


# Light Sensor Setup
light_sensor = ADC(Pin(26))  # Connect the junction of LDR and resistor to pin 26
threshold = 4000  # Set a threshold value for light detection
is_Covered = False

#LED Setups
led1 = PWM(Pin('GPIO0', Pin.OUT))
led1.freq(50)
led1.duty_u16(0)

led2 = PWM(Pin('GPIO1', Pin.OUT))
led2.freq(50)
led2.duty_u16(0)


#Global Variable setup
is_Paused = False
is_Stopped = True
start = False
noteInterval = 0.45
songNo = 0

#mqtt
def callback(topic, msg):
    
    message = msg.decode()
    print((topic.decode(), message))
    
    global start
    global is_Paused
    global is_Stopped
    global noteInterval
    global songNo
    
    if not start:
        print("not started")
#         if message == "Start":
#             print("Start")
#             start = True
#             is_Stopped = False
#             is_Paused = False
    else:
        if message == "Stop":
            print("Stop")
            is_Stopped = True
        else:
            temp = 0.45
            temp = int(message)
            
            
            if temp < 5:
                #Teachable Machines
                print(str(temp))
                songNo = temp
            else:
                #DAHAL Accelerometer
                interval_led(temp)
                print(str(temp))
                
                temp = temp /100
                noteInterval = temp
                print(str(noteInterval))
        
        
        
led2.duty_u16(32000)
client = MQTTClient('Roberto_board', mqtt_broker, port, keepalive=60)
client.connect()
print('Connected to %s MQTT broker' % (mqtt_broker))
client.set_callback(callback)          # set the callback if anything is read
client.subscribe(topic_sub.encode())   # subscribe to a bunch of topics
led2.duty_u16(65500)

#MIDI Constants
NoteOn = 0x90
NoteOff = 0x80
StopNotes = 123
Reset = 0xFF

velocity = {'off':0, 'pppp':8,'ppp':20,'pp':31,'p':42,'mp':53,
    'mf':64,'f':80,'ff':96,'fff':112,'ffff':127}
  
#Bluetooth
p = Yell('Roberto', verbose = True, type = 'midi')
p.connect_up()
led2.duty_u16(0)
time.sleep(2)

#channel stuff
channel = 0
channel = 0x0F & channel

#music meat & potatoes
songs = [
    [  # Original Song
        60, 64, 67, 69, 65, 62, 71, 72, 64, 67, 65, 64, 62, 60, 69, 67
    ],
    [  # Song 1: Arpeggio and leaps
        60, 65, 72, 68, 62, 67, 70, 64, 71, 65, 63, 69, 67, 60, 66, 73
    ],
    [  # Song 2: Random jumps and syncopation feel
        67, 62, 70, 65, 63, 69, 60, 72, 64, 68, 67, 61, 73, 62, 65, 70
    ],
    [  # Song 3: Repeated patterns with variations
        64, 66, 64, 69, 64, 67, 64, 72, 65, 70, 65, 68, 65, 60, 65, 74
    ]
]

# timestamp_ms = time.ticks_ms()
# tsM = (timestamp_ms >> 7 & 0b111111) | 0x80
# tsL =  0x80 | (timestamp_ms & 0b1111111)

# Preload variables
cmd = NoteOn
c =  cmd | channel     
# payload = bytes([tsM,tsL,c,note,velocity['f']])

async def toggle_mqtt():
    while not is_Stopped:
        client.check_msg()
        await asyncio.sleep(0.1)
        

# Read light sensor value, store in boolean
def light_check():
    global is_Covered
    light_value = light_sensor.read_u16()
    print("Light Value:", light_value)  # Debugging output
    if light_value < threshold:
        print("low")
        is_Covered = True
    else:
        print("high")
        is_Covered = False
        
#Initialize with note frequency, returns a PWM for an LED
def frequency_led(freq):
    led1_PWM = int((65535-15000)/(75-55)*freq-123971)
    if led1_PWM > 65535:
        led1_PWM = 65535
    elif led1_PWM < 15000:
        led1_PWM = 15000
    led1.duty_u16(led1_PWM)
    
#Initialize with note interval, returns a PWM for an LED
def interval_led(interval):
    led2_PWM = int((500-65535)/(100-5)*interval+68721)
    print(str(led2_PWM))
    if led2_PWM > 65535:
        led2_PWM = 65535
    elif led2_PWM < 5000:
        led2_PWM = 5000
    led2.duty_u16(led2_PWM)
    


#Main playing loop
async def playback():
    i = 0
    
    global songNo
    global is_Paused
    global is_Stopped
    global is_Covered
    global noteInterval
    
    while not is_Stopped:
        if not is_Paused:
            timestamp_ms = time.ticks_ms()
            tsM = (timestamp_ms >> 7 & 0b111111) | 0x80
            tsL =  0x80 | (timestamp_ms & 0b1111111)

            note = songs[songNo][i]
            
            #led changing to note frequency
            frequency_led(note)
            
            # Note On
            c = cmd | channel
            payload = bytes([tsM,tsL,c, note, velocity['mf']])
            p.send(payload)
            await asyncio.sleep(noteInterval)  # Duration for which the note is played
            
                    
            # Note Off
            c = NoteOff | channel
            payload_off = bytes([tsM,tsL,c, note, velocity['off']])
            p.send(payload_off)
    #         await asyncio.sleep(0.01)  # Short pause before the next note

            i += 1
            if i >= len(songs[songNo]):
                i = 0
        client.check_msg()
        light_check()
        await asyncio.sleep(0.05)
        is_Paused = is_Covered

async def main():
    global start
    global is_Stopped
    global is_Paused
    while not start:
#         client.check_msg()
        start = True
        is_Stopped = False
        is_Paused = False
        await asyncio.sleep(0.05)
    # Create and schedule tasks
    task4 = asyncio.create_task(toggle_mqtt())
    await asyncio.sleep(0.01)
    task1 = asyncio.create_task(playback())
    #task2 = asyncio.create_task(buzzer_cycle())
    #task3 = asyncio.create_task(toggle_flag())
    # Wait for all tasks to complete (they run indefinitely in this case)
    await asyncio.gather(task1, task4)
#     await asyncio.gather(task1, task2, task3, task4)
    #stopper = asyncio.create_task(self.shutdown())
    #await stopper
 
 
try:
    asyncio.run(main())
except Exception as e:
    print(e)
finally:
    p.disconnect()
    client.disconnect()
    led1.duty_u16(0)
