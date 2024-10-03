#Malia Brandt and Roberto Garcia 
#For the Shark and Minnow ME35 Project September 2024
#This code is meant to run on the TM tab of the ME35 pyscript page. The teachable machines 
#detects thumbs up and open palm gestures. For the thumbs up, it send an mqtt message to ME35-24/Malia
#to turn the robot on. For the open palm, it send a mqtt message to turn off. 
from pyscript.js_modules import teach, pose, ble_library, mqtt_library
async def run_model(URL2):
    s = teach.s  # or s = pose.s
    s.URL2 = URL2
    await s.init()
def get_predictions(num_classes):
    predictions = []
    for i in range (0,num_classes):
        divElement = document.getElementById('class' + str(i))
        if divElement:
            divValue = divElement.innerHTML
            predictions.append(divValue)
    return predictions
#initialize mqtt stuff
mqtt_broker = 'broker.hivemq.com'
port = 1883
topic_sub = 'ME35-24/#'       # this reads anything sent to ME35
client = mqtt_library.myClient
print('Connected to %s MQTT broker' % (mqtt_broker))
import asyncio
await run_model("https://teachablemachine.withgoogle.com/models/mykOrHdj6/") #Change to your model link
topic_pub = 'ME35-24/Malia'
while True:
    #if ble.connected:
    #    predictions = get_predictions(2)
    #    send(predictions)
    #await asyncio.sleep(2)
    predictions = get_predictions(2)
    values = [float(item.split(': ')[1]) for item in predictions]
    print(values)
    if values[0] >= 0.90:
        client.publish("ME35-24/Malia", "on")
    elif values[1] >= 0.90:
        client.publish("ME35-24/Malia", "off")
    #else: send nothing
