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
    DCMotor abstractions.
    """

    STOP    = 0
    FORWARD = 1
    REVERSE = -1

    def __init__(self, power_pin: int, forward_pin: int, reverse_pin: int):
        """
        Initializes DCMotor pins as output pins and sets appropriate PWM frequency.
        """
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
        """
        Begins forward driving.
        """
        io.write(self.reverse_pin, LOW)
        io.write(self.forward_pin, HIGH)

    def reverse(self):
        """
        Begins reverse driving.
        """
        io.write(self.forward_pin, LOW)
        io.write(self.reverse_pin, HIGH)

    def stop_rotation(self):
        """
        Stops motor rotation.
        """
        io.write(self.forward_pin, LOW)
        io.write(self.reverse_pin, LOW)

    def stop(self):
        """
        Sets motor duty cycle to 0
        """
        io.set_PWM_dutycycle(self.power_pin, 0)

    def set_power(self, duty_cycle: int):
        """
        Sets motor power. Duty cycle max value = 100
        """
        io.set_PWM_dutycycle(self.power_pin, duty_cycle)

class Servo:
    """
    Servo.
    """

    def __init__(self, pin:int, freq: int = FREQ, max_angle: int = 180):
        """
        Initializes servo pin as output pin and sets PWM frequency. Param `max_angle` = Maximum manufacturer-specified angle of motor.
        That is, the motor range is [0, max_angle]
        """
        io.set_mode(pin, OUTPUT)
        io.set_PWM_frequency(pin, freq)
        self.pin: int = pin
        self.max_angle = max_angle

    def stop(self):
        self.set_pulse_width(0)


    """
    0 -> full counterclockwise
    60 -> center
    120 -> full clockwise
    """
    def set_angle(self, theta: float):
        """Sets motor angle. Ensure inputs are within manufacturer's bounds.
        """

        # Equation derived from relating desired angles to required pulse width.
        # See: https://en.wikipedia.org/wiki/Servo_control#Pulse_duration
        # See: https://en.wikipedia.org/wiki/Pulse-width_modulation
        pulse_width = theta * 1000 / self.max_angle + 1000

        self.set_pulse_width(pulse_width)


    def set_pulse_width(self, width: int):
        """
        Set motor pulse width.
           0    -> off
           1000 -> full counterclockwise
           1500 -> center
           2000 -> full clockwise
        """
        io.set_servo_pulsewidth(self.pin, width)


def cleanup():
    """Releases GPIO resources and stops daemon"""
    print("Releasing GPIO resources... ", end="")
    io.stop()
    os.system("systemctl kill pigpiod")
    os.system("systemctl stop pigpiod") # One of these will get it I'm sure.
    print("DONE")