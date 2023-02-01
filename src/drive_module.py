import RPi.GPIO as GPIO
import time

# GPIO mode should be consistent across all modules
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Steering servo connected to pin GPIO 4
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)

# known calibration settings
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

    def set(self, dc):
        self.pwm.ChangeDutyCycle(dc)

    def shift(self, gear):
        """
        gear 0 = park, 1 = drive, -1 = reverse
        """
        if gear == 0:
            GPIO.output(5, GPIO.LOW)
            GPIO.output(6, GPIO.LOW)
        elif gear == -1:
            GPIO.output(5, GPIO.HIGH)
            GPIO.output(6, GPIO.LOW)
        elif gear == 1:
            GPIO.output(5, GPIO.LOW)
            GPIO.output(6, GPIO.HIGH)
        else:
            raise Exception("unknown gear shift value")

    def forward(self):
        self.shift(1)

    def reverse(self):
        self.shift(-1)

    def park(self):
        self.shift(0)

    def drive(self, cmd):
        """
        normalized driving. 1 is full speed forward, -1 is full speed reverse
        """
        if abs(cmd) < self.cal["tol"]:
            self.park()
            dc = 0
        elif cmd > 0:
            self.forward()
            if cmd > 1:
                cmd = 1
            dc = 0 + cmd * (self.cal["full"])
        else:
            self.reverse()
            if cmd < -1:
                cmd = -1
            dc = 0 - cmd * (self.cal["full"])
        self.set(dc)


def constant_speed():
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


if __name__ == "__main__":
    test_cmd()
    # constant_speed()
