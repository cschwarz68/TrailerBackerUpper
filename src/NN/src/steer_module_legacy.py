"""
IMPORTANT

Restored legacy code. Not refactored. For neural network only.
"""

import RPi.GPIO as GPIO

# GPIO mode should be consistent across all modules
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Steering servo connected to pin GPIO 4
GPIO.setup(4, GPIO.OUT)

# known calibration settings
#steer_cal_35 = {"freq": 35, "center": 2.4, "right": 4, "left": 1.2}
steer_cal_35 = {"freq": 35, "center": 4.6, "right": 6.15, "left": 2.2}

class Steer:
    def __init__(self, cal=steer_cal_35):
        self.cal = cal
        self.pwm = GPIO.PWM(4, cal["freq"])
        self.pwm.start(cal["center"])
        self.current_steering_angle = 90

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

    def steer_by_angle(self, angle, scale=1.0):
        cmd = (angle - 90) / 45
        cmd = cmd * scale
        if cmd > 0:
            if cmd > 1:
                cmd = 1
            dc = self.cal["center"] + cmd * (self.cal["right"] - self.cal["center"])
        else:
            if cmd < -1:
                cmd = -1
            dc = self.cal["center"] - cmd * (self.cal["left"] - self.cal["center"])
        self.set(dc)

    def trailer_steering_test(self, angle):
        cmd = (angle - 90) / 45
        cmd = cmd * 1.5
        if cmd > 0:
            if cmd > 1:
                cmd = 1
            dc = self.cal["center"] + cmd * (self.cal["right"] - self.cal["center"])
        else:
            if cmd < -1:
                cmd = -1
            dc = self.cal["center"] - cmd * (self.cal["left"] - self.cal["center"])
        self.set(dc)
    def stabilize_steering_angle(
        self,
        new_angle,
        num_of_lane_lines,
        max_angle_deviation_two_lines=45,
        max_angle_deviation_one_line=45,
    ):
        if num_of_lane_lines == 2:
            max_angle_deviation = max_angle_deviation_two_lines
        else:
            max_angle_deviation = max_angle_deviation_one_line

        angle_deviation = new_angle - self.current_steering_angle
        if abs(angle_deviation) > max_angle_deviation:
            stabilized_steering_angle = int(
                self.current_steering_angle
                + max_angle_deviation * angle_deviation / abs(angle_deviation)
            )
        else:
            stabilized_steering_angle = new_angle

        self.current_steering_angle = stabilized_steering_angle
        return stabilized_steering_angle


def test_raw():
    steer = Steer()
    cmd = str(steer.cal["center"])
    while cmd != "q":
        steer.set(float(cmd))
        cmd = input("Enter new raw steer command. q to quit:  ")
    steer.stop()
    steer.cleanup()


def test_by_angle():
    steer = Steer()
    cmd = "90"
    while cmd != "q":
        steer.steer_by_angle(float(cmd))
        cmd = input("Enter steering angle 0 - 180. q to quit: ")
    steer.stop()
    steer.cleanup()


def test_cmd():
    steer = Steer()
    cmd = str(0)
    while cmd != "q":
        steer.steer(float(cmd))
        cmd = input("Enter new normalized steer command. q to quit:  ")
    steer.stop()
    steer.cleanup()


if __name__ == "__main__":
    test_cmd()
    #test_raw()
