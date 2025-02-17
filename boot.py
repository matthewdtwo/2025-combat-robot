# boot.py -- run on boot-up
from machine import Pin, PWM

from leds import GREEN, RED, WIFI_AP_ACTIVE, set_leds, wake_animation
import network

from time import sleep

WEAPON_OFF = 98

WEAPON_ON = 75

weapon_servo = PWM(Pin(7), freq=50, duty=WEAPON_OFF)

wake_animation()

# Configure the WiFi access point
ap = network.WLAN(network.AP_IF)
ap.active(True)

ap.config(essid='DomoArigato', password='mrroboto')

# Wait for the AP to be active
while not ap.active():
    sleep(0.1)
    set_leds(WIFI_AP_ACTIVE, RED)


if ap.active():
    set_leds(WIFI_AP_ACTIVE, GREEN)


print('Access Point active')
print('Network config:', ap.ifconfig())

