"""
This module provides abstractions of servos and DC motors.
"""

import gpio as io
import time
import os

os.system("systemctl start pigpiod")
time.sleep(1) # Daemon needs a second to warm up.

io = io.IO()
io.set_PWM_range(9, 100) # Makes it so 50 = 50% duty cycle.

FREQ = 50 # Default PWM frequency.

def cleanup():
    io.stop()
    os.system("systemctl stop pigpiod")
    time.sleep(1)

class DCMotor:
    """
    DCMotor.
    """

    STOP    = 0
    FORWARD = 1
    REVERSE = -1

    def __init__(self, power_pin: int, forward_pin: int, reverse_pin: int, duty_cycle: int = 50):
        self.power = power_pin 
        self.forward_pin = forward_pin
        self.reverse_pin = reverse_pin 

        io.set_output(power_pin)
        io.set_output(forward_pin)
        io.set_output(reverse_pin)

        io.set_PWM_frequency(power_pin, FREQ)
        io.set_PWM_frequency(forward_pin, FREQ)
        io.set_PWM_frequency(reverse_pin, FREQ)

        self.duty_cycle = duty_cycle

    def forward(self):
        io.set_low(self.reverse_pin)
        io.set_high(self.forward_pin)

    def reverse(self):
        io.set_low(self.forward_pin)
        io.set_high(self.reverse_pin)

    def stop_rotation(self):
        io.set_low(self.forward_pin)
        io.set_low(self.reverse_pin)

    def stop(self):
        io.set_PWM_dutycycle(self.power, 0)

    def set_power(self, duty_cycle: int):
        io.set_PWM_dutycycle(self.power, duty_cycle)

class Servo:
    """
    Servo.
    """

    def __init__(self, pin:int, freq: int=FREQ):
        io.set_output(pin)
        self.pin: int = pin
        self.freq = freq

    def stop(self):
        self.set_pulse_width(0)

    def set_angle(self, theta: float):
        width = self.degrees_to_pulse_width(theta)
        self.set_pulse_width(width)

    def degrees_to_pulse_width(self, theta: float):
        pulse = theta * 100 / 9 + 500
        return int(pulse)

    """
    0    -> off
    1000 -> full counterclockwise
    1500 -> center
    2000 -> full clockwise
    """
    def set_pulse_width(self, width: int):
        io.set_servo_pulsewidth(self.pin, width)
