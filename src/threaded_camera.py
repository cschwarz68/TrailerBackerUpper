from picamera2 import Picamera2
from threading import Thread 
from picamera2.encoders import H264Encoder, Quality
import cv2
import numpy as np

import time

class Camera:
   
    def __init__(self, resolution = (640, 480), framerate = 60):
    
        self.frames=0
        self.camera = Picamera2()
        self.config = self.camera.create_video_configuration(main= {"size":resolution})
        self.camera.configure(self.config)

        self.framerate = framerate
        #self.raw_capture = PiRGBArray(self.camera, size = resolution)
        #self.stream = self.camera.capture_continuous(self.raw_capture, format = "bgr", use_video_port = True)

        self.camera.start() 

        time.sleep(1)

        self.camera.set_controls({"AeEnable": False, "AwbEnable":False, "FrameRate": framerate})


        self.frame = None
        self.array = None
        self.stopped = False
    
    def start(self):
        Thread(target=self.update, args = ()).start()
        return self 
    
    def update(self):

        while not self.stopped:
            
            self.frame = self.camera.capture_array()
            
            
            

            
        
        self.camera.close()
        return
            
    def read(self):
        #self.frame = np.rot90(self.frame, 2)
        return self.frame 
    
    def stop(self):
        self.stopped = True

if __name__ == "__main__":
    
    camera = Camera().start()
    time.sleep(7)
    
    start = time.time()
    i = 0
    while time.time()<start+2:
        #before = time.time()
        img=camera.read()
        #after = time.time()
        #cv2.imwrite("image"+ str(i)+".png",img)
        #cv2.imshow("name",img)
        #print("looping",i)
        i+=1
    camera.stop()

    print(camera.frames)
