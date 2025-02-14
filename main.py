import machine
import socket
import network

from time import sleep

# Set up LED on pin 8 (active low)
led = machine.Pin(8, machine.Pin.OUT)
led.value(1)  # Turn off LED initially (active low)

# Load HTML template from file
with open('webpage.html', 'r') as file:
    html = file.read()

# Create socket server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Listening on', addr)


# setup motors

from motor import Motor
# esp32c3 pins
motor_left = Motor(in1=0, in2=1, ena=2, is_left_motor=True) # gray, purple, blue
motor_right = Motor(in1=21, in2=20, ena=10, is_left_motor=False) # green, yellow, orange



# Main server loop
while True:
    try:
        cl, addr = s.accept()
        print('Client connected from', addr)
        request = cl.recv(1024)
        request = str(request)
        
        # Handle button press and release events
        if '/press' in request:
            led.value(0)  # Turn on LED
        elif '/release' in request:
            led.value(1)  # Turn off LED
        
        # Handle joystick position updates
        if '/joystick' in request:
            _, params = request.split('?', 1)
            params = params.split(' ')[0]
            x, y = params.split('&')
            x = float(x.split('=')[1])
            y = float(y.split('=')[1])
            print(f'Joystick position - X: {x}, Y: {y}')

            # Configure motors - note that y is inverted
            left_speed, _ = motor_left.move(x, -y)
            right_speed, _ = motor_right.move(x, -y)
            print(f'Motor speeds - Left: {left_speed}, Right: {right_speed}')
        
        # Send response
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(html)
        cl.close()
        
    except Exception as e:
        print('Error:', e)
        cl.close()