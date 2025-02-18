from machine import Pin
from time import sleep
import neopixel

led_pin = Pin(9)

num_leds = 3

_MAX_BRIGHTNESS = 128

# LEDs
WIFI_AP_ACTIVE = 0
DATA_RECIEVED = 1
WEAPON = 2

ALL_LEDs = [WIFI_AP_ACTIVE, DATA_RECIEVED, WEAPON]

# Colors
OFF = (0, 0, 0)
RED = (_MAX_BRIGHTNESS, 0, 0)
GREEN = (0, _MAX_BRIGHTNESS, 0)
BLUE = (0, 0, _MAX_BRIGHTNESS)

np = neopixel.NeoPixel(led_pin, num_leds)

def all_off():
    for i in range (num_leds):
        np[i] = OFF
    np.write()

def wake_animation():
    for i in range (num_leds):
        np[i] = (_MAX_BRIGHTNESS, _MAX_BRIGHTNESS, _MAX_BRIGHTNESS)
        np.write()
        sleep(0.125)
        np[i] = OFF
        np.write()

    sleep(0.25)

    for i in range (num_leds, 0, -1):
        np[i-1] = (_MAX_BRIGHTNESS, _MAX_BRIGHTNESS, _MAX_BRIGHTNESS)
        np.write()
        sleep(0.125)
        np[i-1] = OFF
        np.write()

def set_leds(led: int | list[int], color):
    if isinstance(led, int):  # Fixed the type check
        np[led] = color
    else:
        for l in led:
            np[l] = color  # Fixed indexing to use l instead of led
    np.write()