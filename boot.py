# boot.py -- run on boot-up
 
import network
import machine
from time import sleep

# Configure the WiFi access point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(ssid='RobotControl')

# Wait for the AP to be active
while not ap.active():
    sleep(0.1)

print('Access Point active')
print('Network config:', ap.ifconfig())
