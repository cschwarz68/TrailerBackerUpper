
from time import time
from threading import Thread
from camera import Camera
from car import Car




# Package Imports
import numpy as np
import cv2
import time

#Local Imports
import image_utils as iu

# Horrible terrible spaghetti code module; will make this all not suck before implementing for real.
# My plan is to implement the functionality of this module main or maybe image processing and then delete this file

class Speedometer:
    

    def __init__(self):
        self.car = Car()
        self.camera = Camera()
        self.last_frame_passed = False
        self.current_frame_passing = False
        self.last_frame = None
        self.current_frame = None
        self.yellow_last_passed_time = 0
        self.rotation_time = 0
        self.last_known_vel = 0
        self.stopped = False
        self.thread = Thread(target=self.update, args = ())

    def start(self):
        self.thread.start()
        return self
    
    def stop(self):
        self.stopped = True
        self.thread.join()
    
    def read(self):
        return self.last_known_vel

    def update(self):
        while not self.stopped:
                
            # filter current frame for yellow and red
            if self.car.current_drive_power == 0:
                self.last_known_vel = 0 # not great
            else:
                self.current_frame = self.camera.read()
                image = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
                yellow = iu.filter_yellow(image)
                red = iu.filter_red(image)
                red_x, red_y = iu.weighted_center(red)
                yellow_x, yellow_y = iu.weighted_center(yellow)
                #combined = iu.combine_images([(yellow,1),(red, 1)])

                

            
            # if yellow and red have same y level (+- 10), then the yellow is passing the red
            # Better pass detection that could be implemented: check if a line drawn from the red intersects the yellow
                if int(yellow_y) in range(int(red_y)-10, int(red_y)+10):
                    self.current_frame_passing = True
                else:
                    self.current_frame_passing = False

                # If the yellow is not passing the red, but it was last frame, a rotation has completed
                if (not self.current_frame_passing) and (self.last_frame_passed):
                    now  = time.time()
                    self.rotation_time = now - self.yellow_last_passed_time # calculate time of rotation
                    self.yellow_last_passed_time = now # set current time of last pass to current time

                if self.current_frame_passing:
                    self.last_frame_passed = True
                else:
                    self.last_frame_passed = False

                if self.rotation_time != 0: # avoid divide by 0 error
                    WHEEL_DIAMETER = 2.5 # inches
                    speed = WHEEL_DIAMETER/self.rotation_time # inches per second
                    self.last_known_vel = speed if self.car.current_drive_power > 0 else speed * -1 # pos for forward; neg for reverse
                
            











        



   
