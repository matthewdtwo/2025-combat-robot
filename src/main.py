import machine
import socket
import json
from config import (LEFT_MOTOR_IN1, LEFT_MOTOR_IN2, LEFT_MOTOR_ENA,
                   RIGHT_MOTOR_IN1, RIGHT_MOTOR_IN2, RIGHT_MOTOR_ENA,
                   ONBOARD_LED_PIN, WEAPON1_ON, WEAPON1_OFF)
from time import sleep, ticks_ms, ticks_diff
from leds import OFF, RED, WEAPON, WIFI_AP_ACTIVE, GREEN, BLUE, set_leds

# Load HTML template from file
with open('webpage.html', 'r') as file:
    html = file.read()

# setup motors
from motor import Motor
motor_left = Motor(in1=LEFT_MOTOR_IN1, in2=LEFT_MOTOR_IN2, ena=LEFT_MOTOR_ENA, is_left_motor=True)
motor_right = Motor(in1=RIGHT_MOTOR_IN1, in2=RIGHT_MOTOR_IN2, ena=RIGHT_MOTOR_ENA, is_left_motor=False)

# setup weapon
led = machine.Pin(ONBOARD_LED_PIN, machine.Pin.OUT)
LED_ARMED = False
WEAPON_ACTIVE = False

# Constants for watchdog
WATCHDOG_TIMEOUT = 500  # 500ms timeout
last_command_time = ticks_ms()


def stop_motors():
    motor_left.stop()
    motor_right.stop()


def check_watchdog(timer):
    global last_command_time
    if ticks_diff(ticks_ms(), last_command_time) > WATCHDOG_TIMEOUT:
        stop_motors()

# Create watchdog timer
watchdog = machine.Timer(0)
watchdog.init(period=100, mode=machine.Timer.PERIODIC, callback=check_watchdog)

def check_wifi_connection(timer):
    global LED_ARMED
    ap_connected = ap.isconnected()
    set_leds(WIFI_AP_ACTIVE, BLUE if ap_connected else GREEN)
    LED_ARMED = ap_connected


check_wifi = machine.Timer(1)
check_wifi.init(period=250, mode=machine.Timer.PERIODIC, callback=check_wifi_connection)


def check_weapon_status(timer):
    global LED_ARMED
    global weapon_servo

    if WEAPON_ACTIVE and LED_ARMED:
        set_leds(WEAPON, BLUE if LED_ARMED else RED)
        print('Weapon Active')
        weapon_servo.on()
        led.value(0)
    else:
        set_leds(WEAPON, GREEN if LED_ARMED else RED)
        weapon_servo.off()
        led.value(1)

weapon_timer = machine.Timer(2)
weapon_timer.init(period=200, mode=machine.Timer.PERIODIC, callback=check_weapon_status)



def send_html(client, html):
    client.send('HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n')
    for i in range(0, len(html), 512):
        client.send(html[i:i+512])

def get_status():
    return json.dumps({
        # 'led': not bool(led.value()),  # Invert since LED is active low
        'led': not led.value(),
        'motors': {
            'left': motor_left.current_speed,
            'right': motor_right.current_speed
        }
    })

def handle_command(path):
    global last_command_time, WEAPON_ACTIVE  # Add WEAPON_ACTIVE as global
    try:
        if path == '/status':
            return get_status()
        elif path.startswith('/button/'):
            last_command_time = ticks_ms()
            state = path.split('/')[-1]
            if state == 'press':
                # on
                WEAPON_ACTIVE = True
            else:
                # off
                WEAPON_ACTIVE = False
            return 'OK'
        
        elif path.startswith('/joystick/'):
            last_command_time = ticks_ms()
            _, x, y = path.split('/')[-3:]
            x, y = float(x), float(y)
            left_speed, _ = motor_left.move(x, -y)
            right_speed, _ = motor_right.move(x, -y)
            return f'L:{left_speed},R:{right_speed}'
    except:
        return 'ERROR'

# Create socket server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print('Listening on', addr)

while True:
    try:
        cl, addr = s.accept()
        request = cl.recv(1024).decode()

        if 'GET / ' in request:
            send_html(cl, html)
        elif 'GET /status' in request or 'GET /button/' in request or 'GET /joystick/' in request:
            path = request.split(' ')[1]
            response = handle_command(path)
            cl.send('HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n')
            cl.send(response)
        
        cl.close()
    except Exception as e:
        print('Error:', e)
        try:
            cl.close()
        except:
            pass