# boot.py -- run on boot-up
import network
import machine
from time import sleep

from leds import GREEN, RED, WIFI_AP_ACTIVE, set_leds, wake_animation
from config import WIRELESS_AP_NAME, WIRELESS_AP_PASS, WEAPON1_PIN, WEAPON1_OFF, WEAPON1_ON

from settings_handler import load_settings

weapon_servo = machine.PWM(machine.Pin(WEAPON1_PIN))
weapon_servo.freq(50)  # 50 Hz for servo control


settings = load_settings()

servo1 = settings.get("servo1", {})

weapon_servo.duty(int(servo1.get("off", WEAPON1_OFF) * 1023 / 180))



wake_animation()

# Configure the WiFi access point
ap = network.WLAN(network.AP_IF)
ap.active(True)

ap.config(essid=WIRELESS_AP_NAME, password=WIRELESS_AP_PASS)

# Wait for the AP to be active
while not ap.active():
    sleep(0.1)
    set_leds(WIFI_AP_ACTIVE, RED)


if ap.active():
    set_leds(WIFI_AP_ACTIVE, GREEN)


print('Access Point active')
print('Network config:', ap.ifconfig())
