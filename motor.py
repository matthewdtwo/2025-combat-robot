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
        self.current_speed = 0.0

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

        # Apply exponential curve to steering input while preserving sign
        x = (abs(x) ** 2) * (1 if x >= 0 else -1)

        # Calculate motor speeds with intermediate clamping
        if self.is_left_motor:
            motor_speed = y + x
        else:
            motor_speed = y - x
            
        # Scale to percentage (-100 to 100)
        motor_speed = motor_speed * 100
        
        # Clamp the final speed to ±100
        motor_speed = max(-100, min(100, motor_speed))

        # Set motor direction and speed based on the sign of motor_speed
        if motor_speed >= 0:
            self.in1_pin.value(1)
            self.in2_pin.value(0)
        else:
            self.in1_pin.value(0)
            self.in2_pin.value(1)

        # Convert speed to PWM duty cycle (use absolute value)
        pwm_duty = int(abs(motor_speed) * 1023 / 100)
        self.ena_pin.duty(pwm_duty)
        
        self.current_speed = motor_speed
        return motor_speed, pwm_duty
