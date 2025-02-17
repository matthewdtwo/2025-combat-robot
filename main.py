import machine
import socket
import json
from time import sleep

# Set up LED on pin 8 (active low)
led = machine.Pin(8, machine.Pin.OUT)
led.value(1)  # Turn off LED initially (active low)

# Load HTML template from file
with open('webpage.html', 'r') as file:
    html = file.read()

# setup motors
from motor import Motor
# esp32c3 pins
motor_left = Motor(in1=0, in2=1, ena=2, is_left_motor=True)
motor_right = Motor(in1=21, in2=20, ena=10, is_left_motor=False)

def send_html(client, html):
    client.send('HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n')
    for i in range(0, len(html), 512):
        client.send(html[i:i+512])

def get_status():
    return json.dumps({
        'led': not bool(led.value()),  # Invert since LED is active low
        'motors': {
            'left': motor_left.current_speed,
            'right': motor_right.current_speed
        }
    })

def handle_command(path):
    try:
        if path == '/status':
            return get_status()
        elif path.startswith('/button/'):
            state = path.split('/')[-1]
            led.value(0 if state == 'press' else 1)
            return 'OK'
        elif path.startswith('/joystick/'):
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