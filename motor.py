from machine import Pin, PWM

class Motor():
    def __init__(self, in1, in2, ena, is_left_motor=True):
        self.in1 = in1
        self.in2 = in2
        self.ena = ena
        self.in1_pin = Pin(in1, Pin.OUT)
        self.in2_pin = Pin(in2, Pin.OUT)
        self.ena_pin = PWM(ena, freq=100, duty=0)
        self.in1_pin.value(0)
        self.in2_pin.value(0)
        self.is_left_motor = is_left_motor

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

        # Calculate base speed from y component
        speed = abs(y) * 100
        turn = abs(x) * 100

        # Calculate motor speed based on whether it's left or right motor
        motor_speed = speed
        if x != 0:  # Turning
            if self.is_left_motor:
                if x < 0:  # Turning left
                    motor_speed = -turn
                elif x > 0:  # Turning right
                    motor_speed = turn
            else:  # Right motor
                if x < 0:  # Turning left
                    motor_speed = turn
                elif x > 0:  # Turning right
                    motor_speed = -turn

        # If moving forward/backward, override turn speed
        if abs(y) > abs(x):
            motor_speed = speed if y > 0 else -speed

        # Set motor direction and speed
        if motor_speed > 0:
            self.in1_pin.value(1)
            self.in2_pin.value(0)
        else:
            self.in1_pin.value(0)
            self.in2_pin.value(1)

        # Convert speed to PWM duty cycle
        pwm_duty = int(abs(motor_speed) * 1023 / 100)
        self.ena_pin.duty(pwm_duty)

        return motor_speed, pwm_duty
