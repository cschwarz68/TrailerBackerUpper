import time
import RPi.GPIO as GPIO

# GPIO mode should be consistent across all modules
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Steering servo connected to pin GPIO 4
GPIO.setup(4, GPIO.OUT)

# known calibration settings
steer_cal_35 = {"freq": 35, "center": 4.2, "right": 5.5, "left": 2.2}


class Steer:
    def __init__(self, cal=steer_cal_35):
        self.cal = cal
        self.pwm = GPIO.PWM(4, cal["freq"])
        self.pwm.start(cal["center"])

    def stop(self):
        self.pwm.stop()

    def cleanup(self):
        GPIO.cleanup()

    def set(self, dc):
        self.pwm.ChangeDutyCycle(dc)

    def steer(self, cmd):
        """
        normalized steering. 1 is full right, -1 is full left
        """
        if cmd > 0:
            if cmd > 1:
                cmd = 1
            dc = self.cal["center"] + cmd * (self.cal["right"] - self.cal["center"])
        else:
            if cmd < -1:
                cmd = -1
            dc = self.cal["center"] - cmd * (self.cal["left"] - self.cal["center"])
        self.set(dc)


def test_raw():
    steer = Steer()
    cmd = str(steer.cal["center"])
    while cmd != "q":
        steer.set(float(cmd))
        cmd = input("Enter new raw steer command. q to quit:  ")
    steer.stop()
    steer.cleanup()


def test_cmd():
    steer = Steer()
    cmd = str(0)
    while cmd != "q":
        steer.steer(float(cmd))
        cmd = input("Enter new raw steer command. q to quit:  ")
    steer.stop()
    steer.cleanup()


if __name__ == "__main__":
    test_cmd()
