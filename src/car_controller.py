import cv2
import numpy as np
import image_processing as ip
import image_utils as iu
from car import Car
from camera import Camera
from speedometer import Speedometer

class CarController:
    def __init__(self):
        self.steering_angle = 0
        self.vel = 0
        self.hitch_angle = 0
        self.lane_pos = 0
        self.trailer_x, self.trailer_y = 0, 0
        self.car = Car()
        self.speedometer = Speedometer().start()


    def update_vel(self):
        self.vel = self.speedometer.read()
    
    def get_vel(self):
        return self.vel

    def update_hitch_angle(self, img: cv2.Mat):
        origin_x, origin_y = img.shape[1] / 2, img.shape[0]
        x_offset, y_offset = self.trailer_x - origin_x, origin_y - self.trailer_y
        angle = np.arctan(x_offset / y_offset)
        angle = np.degrees(angle)
    
    def get_hitch_angle(self):
        return self.hitch_angle
    
    def update_trailer_pos(self, img):
        self.trailer_x, self.trailer_y = ip.weighted_center(iu.filter_red(img))

    def get_trailer_pos(self):
        return self.trailer_x, self.trailer_y

    def update_steering_angle(self):
        self.steering_angle = self.car.current_steering_angle
    
    def get_steering_angle(self):
        return self.steering_angle()



    def stop(self):
        self.speedometer.stop()
    

        

