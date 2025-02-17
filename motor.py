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

        # Calculate base forward/reverse speed from y component
        base_speed = y * 100
        
        # Determine if this is the inside or outside wheel in the turn
        # Inverted logic: positive X = turn right, so right wheel is inside
        is_inside_wheel = (x > 0 and not self.is_left_motor) or (x < 0 and self.is_left_motor)
        turn_amount = abs(x)
        
        if abs(y) > 0.1:  # Moving forward/backward with turn
            if is_inside_wheel:
                # Inside wheel: gradually reduce speed, only reverse at high turn values
                if turn_amount > 0.7:  # Threshold for reversing
                    motor_speed = base_speed * (-1 * (turn_amount - 0.7) / 0.3)  # Gradual reverse
                else:
                    motor_speed = base_speed * (1 - turn_amount)  # Gradual slowdown
            else:
                # Outside wheel: maintain full power
                motor_speed = base_speed
        else:  # Pure rotation (no forward/backward motion)
            if is_inside_wheel:
                motor_speed = -100 * turn_amount
            else:
                motor_speed = 100 * turn_amount

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
        
        self.current_speed = motor_speed
        return motor_speed, pwm_duty
