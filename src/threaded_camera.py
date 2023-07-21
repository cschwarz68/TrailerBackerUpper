# Support for the `picamera` moudle has ended. `picamera2`` aims to replace it using the new libcamera system`
# Unfortunately, `picamera2` is in very early stages of development. It does seem to be quite slow, but that might just be my fault
# for coding poorly. In any case, the interface for controlling the camera's settings is very confusing.
# Please consult https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf before making any crazy changes in this module.

from picamera2 import Picamera2
from threading import Thread 
import libcamera
import numpy as np

import time


class Camera:
   
    def __init__(self, resolution = (640, 480), framerate = 60):
    
        self.frames=0
        self.camera = Picamera2()
        self.config = self.camera.create_video_configuration(main= {"size":resolution})
        self.config["transform"] = libcamera.Transform(hflip=True,vflip=True)
        self.camera.configure(self.config)

        self.framerate = framerate
      

        self.camera.start()

        time.sleep(2) # Needs a moment to get ready.

        self.camera.set_controls({"AeEnable": False, "AwbEnable":False, "FrameRate": framerate}) 
        # See page 69 (ha) of https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf for camera control information
        # (Appendix C: Camera controls)

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