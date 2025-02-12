import machine
import socket
import network

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

# Load HTML template from file
with open('webpage.html', 'r') as file:
    html = file.read()

# Create socket server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Listening on', addr)

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
        
        # Send response
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(html)
        cl.close()
        
    except Exception as e:
        print('Error:', e)
        cl.close()