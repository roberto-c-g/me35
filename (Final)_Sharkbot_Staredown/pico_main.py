from machine import Pin, PWM, deepsleep
import time
import BLE_CEEO as BLE_CEEO
import machine
import neopixel

# Setup
buzzer = PWM(Pin(18, Pin.OUT))
led_2 = Pin(16, Pin.OUT)
led_1 = Pin(17, Pin.OUT)
button = Pin(14, Pin.IN, Pin.PULL_DOWN)
f0 = machine.Pin('GPIO0', machine.Pin.OUT)
f0.off()
f1 = machine.Pin('GPIO1', machine.Pin.OUT)
f1.off()
f2 = machine.Pin('GPIO2', machine.Pin.OUT)
f2.off()
f3 = machine.Pin('GPIO3', machine.Pin.OUT)
f3.off()
f4 = machine.Pin('GPIO4', machine.Pin.OUT)
f4.off()
state = (0,0,0)  # RGB
neo = neopixel.NeoPixel(Pin(28),1)
neo[0] = state
neo.write()

# BLE Peripheral
pico_ble = BLE_CEEO.Yell(name='Pico', verbose=True)

# Globals
game_active = False

# Function to handle received BLE messages
def on_ble_rx(data):
    global game_active
    print("a")
    print("b")
    print("c")
    message = data.decode('utf-8')
    print("0000")
    print(f"Received message: {message}")
    print("you made it?")
    
    if message == "movement_detected" and game_active:
        print("Movement detected! Buzzing and flashing red.")
        #flash_red()
        buzz()
        #end_game()
    elif message == "red_light" and game_active:
        print("d")
        led_2.on()
        led_1.on()
    elif message == "green_light":
        print("e")
        led_1.off()
        led_2.off()

# Function to buzz
def buzz():
    buzzer.freq(300)
    buzzer.duty_u16(30000)
    time.sleep(0.5)
    buzzer.duty_u16(0)

# Function to buzz with a happy sound
def buzz_happy():
    melody = [262, 294, 330, 349, 392]  # Notes: C, D, E, F, G
    duration = 0.2

    for note in melody:
        buzzer.freq(note)
        buzzer.duty_u16(30000)
        time.sleep(duration)
        buzzer.duty_u16(0)
        time.sleep(0.05)

def buzz_start():
    duration = 0.5
    buzzer.freq(165)
    buzzer.duty_u16(30000)
    time.sleep(duration)
    buzzer.duty_u16(0)
    time.sleep(0.05)
    buzzer.freq(185)
    buzzer.duty_u16(30000)
    time.sleep(duration)
    buzzer.duty_u16(0)

# Function to flash red LED
def flash_red():
    for _ in range(3):
        led_2.on()
        led_1.on()
        time.sleep(0.3)
        led_2.off()
        led_1.off()
        time.sleep(0.3)

# Function to check button press
def button_pressed():
    return button.value() == 1

# Start game
def start_game():
    global game_active
    print("Game started!")
    buzz_start()
    game_active = True

# End game
def end_game():
    global game_active
    print("Game ended.")
    game_active = False
    buzz_happy()  # Play the happy sound

# Idle mode waiting for button press
def idle_mode():
    print("Idle mode. Press the button to start the game.")
    led_2.on()
    while not button_pressed():
        time.sleep(0.1)
    time.sleep(0.5)
    

# Ensure BLE connection
def ensure_ble_connection():
    print("Ensuring BLE connection...") 
    while not pico_ble.is_connected:
        f0.on()
        time.sleep(0.1)
        print("Attempting to connect...")
        f1.on()
        time.sleep(0.1)
        pico_ble.connect_up()
        if pico_ble.is_connected:
            print("Connected successfully.")
            f2.on()
            f1.off()
            f3.off()
            time.sleep(0.1)  
        else:
            print("Connection failed. Retrying in 1 second...")
            f2.off()
            f3.on()
            time.sleep(1)
            f3.off()

# Check bluetooth connection
def check_connection():
    if not pico_ble.is_connected:
            f3.on()
            f2.off()
            f1.off()
    print("good")

# Main program
try:
    if __name__ == "__main__":
        pico_ble._write_callback = on_ble_rx
        ensure_ble_connection()  # Establish and maintain BLE connection

        while True:
            check_connection()
            if not game_active:
                idle_mode()  # Wait for button press to start the game
                start_game()  # Begin the game
            else:
                if button_pressed():
                    print("Button pressed during game!")
                    end_game()  # End the game on button press
                    time.sleep(0.5)

            # Keep the program alive and BLE communication running
            time.sleep(0.1)
finally:
    f4.on()
    f3.on()
    f2.off()
    f1.off()
    f0.off()
