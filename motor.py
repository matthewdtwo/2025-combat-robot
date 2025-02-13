from machine import Pin, PWM

class Motor():
    def __init__(self, in1, in2, ena):
        self.in1 = in1
        self.in2 = in2
        self.ena = ena
        self.in1_pin = Pin(in1, Pin.OUT)
        self.in2_pin = Pin(in2, Pin.OUT)
        self.ena_pin = PWM(ena, freq=500, duty=0)
        self.in1_pin.value(0)
        self.in2_pin.value(0)

    def forward(self, speed):
        # scale speed between 0 and 1023
        speed = int(speed * 1023 / 100)

        self.in1_pin.value(1)
        self.in2_pin.value(0)
        self.ena_pin.duty(speed)
    
    def reverse(self, speed):
        # scale speed between 0 and 1023
        speed = int(speed * 1023 / 100)

        self.in1_pin.value(0)
        self.in2_pin.value(1)
        self.ena_pin.duty(speed)

    def stop(self):
        self.in1_pin.value(0)
        self.in2_pin.value(0)
        self.ena_pin.duty(0)

    def move(self, x, y):
        # Ensure x and y are within the range -1 to 1
        x = max(-1, min(1, x))
        y = max(-1, min(1, y))

        # Calculate speed for each motor
        left_speed = (y + x) * 50  # Scale to percentage
        right_speed = (y - x) * 50  # Scale to percentage

        # Determine direction and set motor speeds
        if left_speed > 0:
            self.forward(left_speed)
        else:
            self.reverse(-left_speed)

        if right_speed > 0:
            self.forward(right_speed)
        else:
            self.reverse(-right_speed)

        return left_speed, right_speed
