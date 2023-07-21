import warnings
import math
from time import time_ns, time, sleep
from threading import Thread
from threaded_camera import Camera
from car import Car
from streaming import FrameSegment
import socket




# Package Imports
import numpy as np
import cv2
import time

#Local Imports
import image_utils as iu

# Horrible terrible spaghetti code module; will make this all not suck before implementing for real.
# My plan is to implement the functionality of this module main or maybe image processing and then delete this file

class SpeedDetector:
    

    def __init__(self):
        #idk if I need anything in here yet
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

                if self.rotation_time != 0:
                    speed = 2.5/self.rotation_time #2.5 is wheel diameter in inches, speed is in inches per second
                    self.last_known_vel = speed if self.car.current_drive_power > 0 else speed * -1
                
            













    

def update_image(cam: Camera):
    
    image = cam.read()
    
    
    filtered = iu.filter_yellow(image)
    return filtered

   
def go():
    detector = SpeedDetector()
    time.sleep(3)
    while True:
        detector.update()
      
        



def stream_to_client(stream_image: cv2.Mat):
    frame_segment
   
    frame_segment.udp_frame(stream_image)   

if __name__ == "__main__":
    # Streaming
    avg_color = 0
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    port = 25565
    """
    IMPORTANT

    Insert the IP address of the device to stream to.
    """
    addr = "192.168.2.185"
    frame_segment = FrameSegment(server_socket, port, addr)

    go()

   
