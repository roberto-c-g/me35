
from pyscript.js_modules import teach, pose, mqtt_library

#ble = ble_library.newBLE()
myClient = mqtt_library.myClient("broker.hivemq.com", 8884)
mqtt_connected = False
sub_topic = 'ME35-24/Roberto'
pub_topic = 'ME35-24/Roberto'

async def received_mqtt_msg(message):
    message = myClient.read().split('	')  #add here anything you want to do with received messages

async def run_model(URL2):
    s = teach.s  # or s = pose.s
    s.URL2 = URL2
    await s.init()
    
async def connect(name):
    global mqtt_connected
    myClient.init()
    while not myClient.connected:
        await asyncio.sleep(2)
    myClient.subscribe(sub_topic)
    myClient.callback = received_mqtt_msg
    mqtt_connected = True
        
async def disconnect():
    print('disconnected')

def send(message):
    print('sending ', message)
    myClient.publish(pub_topic, message)

def get_predictions(num_classes):
    predictions = []
    for i in range (0,num_classes):
        divElement = document.getElementById('class' + str(i))
        if divElement:
            divValue = divElement.innerHTML
            predictions.append(divValue)
    return predictions

import asyncio
await run_model("https://teachablemachine.withgoogle.com/models/6O2pBccPr/")
await connect('RobertoTM')

while True:
    if mqtt_connected:
        predictions = get_predictions(5)
        values = [float(item.split(': ')[1]) for item in predictions]
        if values[0] >= 0.90:
            send("0")
        elif values[1] >= 0.90:
            send("1")
        elif values[2] >= 0.90:
            send("2")
        elif values[3] >= 0.90:
            send("3")
        else:
            print("No change")
    await asyncio.sleep(1)
