from machine import Pin, PWM

class Servo:
    def __init__(self, pin, start_pos, stop_pos, freq=50):
        self.start_pos = start_pos
        self.stop_pos = stop_pos
        self.freq = freq
        self.pwm = PWM(Pin(pin), freq=freq, duty=start_pos)
        self.current_pos = start_pos
        
    def on(self):
        self.current_pos = self.start_pos
        self.pwm.duty(self.start_pos)
        
    def off(self):
        self.current_pos = self.stop_pos
        self.pwm.duty(self.stop_pos)
        
    def set_position(self, position):
        self.current_pos = position
        self.pwm.duty(position)
