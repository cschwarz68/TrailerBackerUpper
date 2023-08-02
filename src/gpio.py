"""
This module provides abstractions of servos and DC motors.
"""

from pigpio import pi, OUTPUT, LOW, HIGH
import time
import os

os.system("systemctl start pigpiod")
time.sleep(1) # Daemon needs a second to warm up.

io = pi()
io.set_PWM_range(9, 100) # Makes it so 50 = 50% duty cycle.

FREQ = 50 # Default PWM frequency.

class DCMotor:
    """
    DCMotor.
    """

    STOP    = 0
    FORWARD = 1
    REVERSE = -1

    def __init__(self, power_pin: int, forward_pin: int, reverse_pin: int):
        self.power_pin = power_pin 
        self.forward_pin = forward_pin
        self.reverse_pin = reverse_pin 

        io.set_mode(power_pin, OUTPUT)
        io.set_mode(forward_pin, OUTPUT)
        io.set_mode(reverse_pin, OUTPUT)

        io.set_PWM_frequency(power_pin, FREQ)
        io.set_PWM_frequency(forward_pin, FREQ)
        io.set_PWM_frequency(reverse_pin, FREQ)

        

    def forward(self):
        io.write(self.reverse_pin, LOW)
        io.write(self.forward_pin, HIGH)

    def reverse(self):
        io.write(self.forward_pin, LOW)
        io.write(self.reverse_pin, HIGH)

    def stop_rotation(self):
        io.write(self.forward_pin, LOW)
        io.write(self.reverse_pin, LOW)

    def stop(self):
        io.set_PWM_dutycycle(self.power_pin, 0)

    def set_power(self, duty_cycle: int):
        io.set_PWM_dutycycle(self.power_pin, duty_cycle)

class Servo:
    """
    Servo.
    """

    def __init__(self, pin:int, freq: int = FREQ):
        io.set_mode(pin, OUTPUT)
        io.set_PWM_frequency(pin, freq)
        self.pin: int = pin

    def stop(self):
        self.set_pulse_width(0)


    """
    0 -> full counterclockwise
    60 -> center
    120 -> full clockwise
    """
    def set_angle(self, theta: float):

        # Equation derived from relating desired angles to required pulse width.
        # See: https://en.wikipedia.org/wiki/Servo_control#Pulse_duration
        # See: https://en.wikipedia.org/wiki/Pulse-width_modulation
        pulse_width = theta * 25 / 3 + 1000

        self.set_pulse_width(pulse_width)


    """
    0    -> off
    1000 -> full counterclockwise
    1500 -> center
    2000 -> full clockwise
    """
    def set_pulse_width(self, width: int):
        io.set_servo_pulsewidth(self.pin, width)


def cleanup():
    """Releases GPIO resources and stops daemon"""
    print("Releasing GPIO resources... ", end="")
    io.stop()
    os.system("systemctl kill pigpiod")
    os.system("systemctl stop pigpiod")
    print("DONE")