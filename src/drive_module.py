"""
This code is for controlling a robot car with a Raspberry Pi using the RPi.GPIO library. 
It defines a class called Drive which represents the car's drivetrain and provides methods to control it. 
The Drive class has methods to set the speed of the car, shift gears (park, drive, reverse), and to stop and clean up the GPIO pins. 
It uses PWM (pulse width modulation) to control the speed of the motor.

The code also imports the module steer_module for controlling the car's steering via. servo motor. 
It defines three test methods to test the car's raw drive command, normalized drive command, and steering and driving simultaneously.

Finally, the code checks if it is being run as the main script and runs the test_steer_and_drive() method which tests both steering and driving 
at the same time by setting the car to drive at a constant speed and turning the steering servo to the right.
"""

import RPi.GPIO as GPIO
import time

# Local Imports
import steer_module as sr

# GPIO mode should be consistent across all modules.
GPIO.setmode(GPIO.BCM) # Pin numbering system: Broadcom SOC
# GPIO.setwarnings(False) # Disables warnings for pin configuration conflicts.

# Drive control wires
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)

# Known calibration settings.
#                frequency | max. speed| amount joystick needs to be pushed to drive (prevents drift)
drive_cal_50 = {"freq": 50, "full": 50, "tol": 1e-3}

class Drive:
    def __init__(self, cal=drive_cal_50):
        self.cal = cal
        self.pwm = GPIO.PWM(25, cal["freq"])
        self.pwm.start(0)

    def stop(self):
        self.pwm.stop()

    def cleanup(self):
        GPIO.cleanup()

    def set(self, duty_cycle):
        self.pwm.ChangeDutyCycle(duty_cycle)

    def shift(self, gear):
        # Gears: 0 --> park, 1 --> drive, -1 --> reverse
        if gear == 0:
            GPIO.output(5, GPIO.LOW)
            GPIO.output(6, GPIO.LOW)
        elif gear == 1:
            GPIO.output(5, GPIO.LOW)
            GPIO.output(6, GPIO.HIGH)
        elif gear == -1:
            GPIO.output(5, GPIO.HIGH)
            GPIO.output(6, GPIO.LOW)
        else:
            raise Exception("Unknown gear shift value.")

    def forward(self):
        self.shift(1)

    def reverse(self):
        self.shift(-1)

    def park(self):
        self.shift(0)

    def drive(self, power):
        # Normalized driving. 1 is full speed forward, -1 is full speed reverse.
       duty_cycle = 25 * power - 25
       self.set(duty_cycle)


def constant_speed():
    print("test: constant_speed")
    drive = Drive()
    while True:
        drive.drive(0.8)
        time.sleep(3)
        drive.drive(0.5)


def test_raw():
    drive = Drive()
    cmd = str(0)
    while cmd != "q":
        drive.set(float(cmd))
        cmd = input("Enter new raw drive command. q to quit:  ")
    drive.stop()
    drive.cleanup()


def test_cmd():
    drive = Drive()
    cmd = str(0)
    while cmd != "q":
        drive.drive(float(cmd))
        cmd = input("Enter new normalized drive command. q to quit:  ")
    drive.stop()
    drive.cleanup()

def test_steer_and_drive():
    drive = Drive()
    steer = sr.Steer()
    while True:
        drive.drive(0.8)
        steer.set(4.6)


if __name__ == "__main__":
    # test_cmd()
    constant_speed()
    #test_steer_and_drive()