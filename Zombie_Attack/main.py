import time
import asyncio
from Tufts_ble3 import Sniff, Yell
import machine
from machine import Pin, PWM 
import neopixel

global zomnum
led = neopixel.NeoPixel(Pin(28),1)
buzzer = PWM(Pin('GPIO18', Pin.OUT))
buzzer.freq(440)
led1= Pin('GPIO0', Pin.OUT)

# Global array to keep track of tag counts
arr = [
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    [0] * 13  # Initialize second row with zeros
]

# Dictionary to track active sync_sniff tasks
active_tasks = {}

async def sync_sniff(z_tag, sniff_instance):
    print(f"Checking connection for tag: {z_tag}")
    await asyncio.sleep(3)
    #z = Sniff(z_tag, verbose=False)
    #z.scan(0)
    latest = sniff_instance.last
    if latest != z_tag:
        print(f"No signal for tag: {z_tag}")
        return
    else:
        print(f"Signal received for tag: {z_tag}")
        numb = z_tag.replace('!', '')
        placen = int(numb) - 1  # Adjust for zero-indexing
        if 0 <= placen < len(arr[1]):
            arr[1][placen] += 1
            print(f"Updated counts for tag {numb}: {arr}")
            buzzer.duty_u16(1000)
            led1.on()
        await asyncio.sleep(0.1)  # Non-blocking sleep for 0.1 seconds
        buzzer.duty_u16(0)
        led1.off()
        return

    # Update the count for the detected tag
    

    # Remove the tag from active tasks
    del active_tasks[z_tag]

async def central():
    human = True
    c = Sniff('!', verbose=False)
    c.scan(0)  # Start scanning
    
    while human:
        print(c.last_rssi)
    	led[0]=(255,0,0)
    	led.write()

        latest = c.last
        c.last=''
        if latest and latest != '' and c.last_rssi>-60:
            if latest not in active_tasks:  # Only create a task if not already running
                print("Detected tag:", latest)
                active_tasks[latest] = asyncio.create_task(sync_sniff(latest, c))  # Track the task
                
        # Check if a tag is still active in the task
        for tag in list(active_tasks.keys()):
            if active_tasks[tag].done():  # If the task has completed
                del active_tasks[tag]  # Remove the completed task from active tasks
        for i in range(13):
            if arr[1][i-1]>=3 and i!=10:
                human=False
                global zombnum
                zombnum=arr[0][i-1]
        await asyncio.sleep(0.5)  # Non-blocking sleep for 0.1 seconds

# Uncomment to use the peripheral function
def peripheral(numb_zom):    
    p = Yell()
    led[0]=(0,255,0)
    led.write()
    buzzer.duty_u16(1000)
    try:    
        while True:
            p.advertise(f'!{numb_zom}')
            print(numb_zom)
            time.sleep(0.1)  # Keep this blocking as it's run sequentially
    finally:
        p.stop_advertising()
        buzzer.duty_u16(0)
        led[0]=(0,0,0)
        led.write()

# Entry point for async execution
async def main():
    print("Starting main function")
    await central()

# Start the async event loop
asyncio.run(main())
print(zombnum)
peripheral(zom_num)
