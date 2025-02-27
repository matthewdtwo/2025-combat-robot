import machine
import socket
import json
from config import (LEFT_MOTOR_IN1, LEFT_MOTOR_IN2, LEFT_MOTOR_ENA,
                   RIGHT_MOTOR_IN1, RIGHT_MOTOR_IN2, RIGHT_MOTOR_ENA,
                   ONBOARD_LED_PIN, WEAPON1_ON, WEAPON1_OFF, REVERSE_STEERING, REVERSE_FORWARD)
from time import sleep, ticks_ms, ticks_diff
from leds import OFF, RED, WEAPON, WIFI_AP_ACTIVE, GREEN, BLUE, set_leds
from servo_handler import load_settings, save_settings

# Load HTML template from file
with open('webpage.html', 'r') as file:
    html = file.read()

# setup motors
from motor import Motor
motor_left = Motor(in1=LEFT_MOTOR_IN1, in2=LEFT_MOTOR_IN2, ena=LEFT_MOTOR_ENA, is_left_motor=True)
motor_right = Motor(in1=RIGHT_MOTOR_IN1, in2=RIGHT_MOTOR_IN2, ena=RIGHT_MOTOR_ENA, is_left_motor=False)

# setup weapon
led = machine.Pin(ONBOARD_LED_PIN, machine.Pin.OUT)
WEAPON_ARMED = False
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
    global WEAPON_ARMED
    ap_connected = ap.isconnected()
    set_leds(WIFI_AP_ACTIVE, BLUE if ap_connected else GREEN)
    WEAPON_ARMED = ap_connected


check_wifi = machine.Timer(1)
check_wifi.init(period=250, mode=machine.Timer.PERIODIC, callback=check_wifi_connection)


def check_weapon_status(timer):
    global WEAPON_ARMED
    global weapon_servo
    global weapon_servo2

    if WEAPON_ACTIVE and WEAPON_ARMED:
        set_leds(WEAPON, BLUE if WEAPON_ARMED else RED)
        print('Weapon Active')
        weapon_servo.on()
        weapon_servo2.on()
        led.value(0)
    else:
        set_leds(WEAPON, GREEN if WEAPON_ARMED else RED)
        weapon_servo.off()
        weapon_servo2.off()
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

def handle_command(path, request_type='GET', body=None):
    global last_command_time, WEAPON_ACTIVE
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
            x = -x if REVERSE_STEERING else x  # Reverse steering if configured
            y = -y if REVERSE_FORWARD else y   # Reverse forward/back if configured
            left_speed, _ = motor_left.move(x, -y)
            right_speed, _ = motor_right.move(x, -y)
            return f'L:{left_speed},R:{right_speed}'
            
        elif path == '/servo/settings':
            if request_type == 'GET':
                # Return current servo settings
                return json.dumps(load_settings())
            elif request_type == 'POST' and body:
                try:
                    # Parse received JSON
                    settings = json.loads(body)
                    
                    # Validate settings
                    required_keys = ['servo1', 'servo2']
                    for key in required_keys:
                        if key not in settings:
                            return json.dumps({"error": f"Missing required key: {key}"})
                        if 'on' not in settings[key] or 'off' not in settings[key]:
                            return json.dumps({"error": f"Missing on/off values for {key}"})
                    
                    # Save settings
                    save_settings(settings)
                    return json.dumps({"success": "Settings saved successfully"})
                except Exception as e:
                    return json.dumps({"error": f"Error processing settings: {str(e)}"})
    except Exception as e:
        print("Command error:", e)
        return json.dumps({"error": str(e)})

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
        request_lines = request.split('\r\n')
        request_line = request_lines[0] if request_lines else ""
        
        # Parse request type and path
        parts = request_line.split(' ')
        if len(parts) >= 2:
            request_type = parts[0]  # GET or POST
            path = parts[1]          # URL path
            
            # Handle GET requests
            if request_type == 'GET':
                if path == '/':
                    send_html(cl, html)
                else:
                    response = handle_command(path, request_type)
                    cl.send('HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n')
                    cl.send(response)
            
            # Handle POST requests
            elif request_type == 'POST':
                # Find Content-Length header to determine request body size
                content_length = 0
                for line in request_lines:
                    if line.lower().startswith('content-length:'):
                        content_length = int(line.split(':')[1].strip())
                        break
                
                # Get request body
                body = None
                if content_length > 0:
                    # Find the empty line that separates headers from body
                    empty_line_pos = request.find('\r\n\r\n')
                    if empty_line_pos != -1:
                        body_start = empty_line_pos + 4
                        body = request[body_start:body_start+content_length]
                
                response = handle_command(path, request_type, body)
                cl.send('HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n')
                cl.send(response)
            
        cl.close()
    except Exception as e:
        print('Error:', e)
        try:
            cl.close()
        except:
            pass