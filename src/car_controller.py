import cv2
import numpy as np
import image_processing as ip
import image_utils as iu
from car import Car
from speedometer import SpeedDetector

class CarController:
    steering_angle = 0
    vel = 0
    hitch_angle = 0
    lane_pos = 0
    trailer_x, trailer_y = 0, 0
    car = Car()
    speedometer = SpeedDetector().start()


    def update_vel(self):
        self.vel = self.speedometer.read()
        return self.vel

    def update_hitch_angle(self, img: cv2.Mat):
        origin_x, origin_y = img.shape[1] / 2, img.shape[0]
        x_offset, y_offset = self.trailer_x - origin_x, origin_y - self.trailer_y
        angle = np.arctan(x_offset / y_offset)
        angle = np.degrees(angle)
        return angle
    
    def update_trailer_pos(self, img):
        self.trailer_x, self.trailer_y = ip.weighted_center(iu.filter_red(img))

    def update_steering_angle(self):
        self.steering_angle = self.car.current_steering_angle

    def stop(self):
        self.speedometer.stop()
    

        

