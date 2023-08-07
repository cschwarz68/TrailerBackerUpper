
from time import time
from threading import Thread
from camera import Camera
from truck import Truck




# Package Imports
import numpy as np
import cv2
import time
from gamepad import Gamepad, Inputs

#Local Imports
import image_utils as iu
from streaming import UDPStreamer
#streamer = Streamer()

# This module calculates the speed of the vehicle by observing a marker on one of the trailer wheels. When the marker
# passes a refernce point, the time since the last pass is recorded. Speed is calculated by dividing wheel diameter by
# rotation time.
# Major limitations:
#   The speed can only update as fast as the wheel rotates.
#   At high speeds, the wheel rotates too fast for the camera to process.

class Speedometer:
    

    def __init__(self):
        self.truck = Truck()
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
        print("Releasing speedometer resources... ", end="")
        self.stopped = True
        self.thread.join()
        print("DONE")
    
    def read(self):
        return self.last_known_vel

    def update(self):
        while not self.stopped:
                
            # filter current frame for yellow and red
            if self.truck.current_drive_power == 0:
                self.last_known_vel = 0 # not great
            else:
                self.current_frame = self.camera.read()
                image = self.current_frame # cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
                yellow = iu.filter_yellow(image)
                red = iu.filter_red(image)
                red_x, red_y = iu.weighted_center(red)
                yellow_x, yellow_y = iu.weighted_center(yellow)
                combined = iu.combine_images([(yellow,1),(red, 1)])
                #streamer.stream_image(combined)


                

            
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
                    self.last_known_vel = speed if self.truck.current_drive_power > 0 else speed * -1 # positive for forward; negative for reverse

if __name__ == "__main__":
    cam = Camera().start()
    speedometer = Speedometer().start()
    streamer = UDPStreamer()
    g = Gamepad()
    car = Truck()
    while True:
        g.update_input()
        img = cam.read()
        speed = speedometer.read()
        iu.put_text(img, f"Speed: {speed}")
        streamer.stream_image(img)
        stick_val = g.get_stick_value(Inputs.LX)
        trigger_val = g.get_trigger_value()
        if stick_val is not None:
            car.gamepad_steer(stick_val)
        if trigger_val is not None:
            car.gamepad_drive(trigger_val)
        if g.was_pressed(Inputs.B):
            break
        

                
            











        



   
