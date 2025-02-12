# boot.py -- run on boot-up
 
import network
import machine
from time import sleep

# Configure the WiFi access point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(ssid='ESP-AP')

# Wait for the AP to be active
while not ap.active():
    sleep(0.1)

print('Access Point active')
print('Network config:', ap.ifconfig())

# Set up LED on pin 8 (active low)
led = machine.Pin(8, machine.Pin.OUT)
led.value(1)  # Turn off LED initially (active low)
sleep(0.25)
for _ in range(3):
    led.value(0)
    sleep(0.25)
    led.value(1)
    sleep(0.25)