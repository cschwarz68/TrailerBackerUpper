import cv2
import numpy as np
import image_processing as ip
import image_utils as iu
from car import Car
from camera import Camera
from speedometer import Speedometer

# TODO: Come up with a nice name for this module and class

class CarController:
    def __init__(self):
        self.steering_angle = 0
        self.vel = 0
        self.hitch_angle = 0
        self.lane_pos = 0
        self.trailer_x, self.trailer_y = 0, 0
        self.car = Car()
        self.cam = Camera()
        self.frame = self.cam.read() # ensure frame is non-None at start
        self.speedometer = Speedometer().start()
        self.lanes = []


    def update_vel(self):
        self.vel = self.speedometer.read()
    
    def get_vel(self):
        return self.vel

    def update_hitch_angle(self):
        img: cv2.Mat = self.frame
        origin_x, origin_y = img.shape[1] / 2, img.shape[0]
        x_offset, y_offset = self.trailer_x - origin_x, origin_y - self.trailer_y
        angle = np.arctan(x_offset / y_offset)
        angle = np.degrees(angle)
    
    def get_hitch_angle(self):
        return self.hitch_angle
    
    def update_trailer_pos(self):
        img = self.frame
        red = iu.filter_red(img)
        trailer_x, trailer_y = ip.weighted_center(red) # relative to frame; needs to be relative to lane center
        

    def get_trailer_pos(self):
        return self.trailer_x, self.trailer_y

    def update_steering_angle(self):
        self.steering_angle = self.car.current_steering_angle
    
    def get_steering_angle(self):
        return self.steering_angle()
    
    def read_camera(self):
        self.frame = self.cam.read()

    def update_state(self):
        self.read_camera()
        self.update_vel()
        self.update_hitch_angle()
        self.update_steering_angle()
        self.update_trailer_pos()

    def stop(self):
        self.speedometer.stop()

    

        

