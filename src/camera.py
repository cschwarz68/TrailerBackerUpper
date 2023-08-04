# Support for the `picamera` moudle has ended. `picamera2` aims to replace it using the new libcamera system
# Unfortunately, `picamera2` is in very early stages of development. It does seem to be quite slow, but that might just be my fault
# for coding poorly. In any case, the interface for controlling the camera's settings is very confusing.
# Please consult https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf before making any crazy changes in this module.

from picamera2 import Picamera2
from threading import Thread 
import libcamera
import cv2

import time

from constants import CameraSettings


class Camera:
     
    _self = None
    camera = None

    def __new__(cls):
        # Ensures only one instance of Camera exists at one time. Any module creating a camera object references the SAME camera. This is very useful.
        # Once second camera is set up I will make two children of this class (one for each camera), and those classes will be singletons.
        if cls._self is None:
            cls._self = super().__new__(cls)

        return cls._self
   
    def __init__(self, resolution = CameraSettings.RESOLUTION, framerate = CameraSettings.FRAMERATE):
    
        if self.camera is None:
            self.camera = Picamera2()
            self.thread = Thread(target=self.update, args = ())

        if not self.camera.started:
            self.config = self.camera.create_video_configuration(main= {"size":resolution})
            self.config["transform"] = libcamera.Transform(hflip=True,vflip=True) # 180 degree rotation since the camera is upside-down.
            self.camera.configure(self.config)

        

        self.camera.start()

        time.sleep(2) # Needs a moment to get ready; doucmentations says to do this.
        self.camera.set_controls({"AeEnable": True, "AwbEnable": True, "FrameRate": framerate})

        # AeEnable and AwbEnable control automatic exposure control and automatic white balancing. Picamera2 documentations reccomends these be off for video.
        # Unsure how much of a performance benefit this gives us.
        # Gaussian blur settings for lane detection had to be adjusted due to decreased image brightness as a result of changing these settings.

        # See page 69 (ha) of https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf for more camera control information
        # (Appendix C: Camera controls)

        bgr= self.camera.capture_array() # initialize camera with non-None frame
        self.frame = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        self.stopped = False
    
    def start(self):
        # If the camera is to be used by multiple python modules, only the *first* one should call `start()`, the others can
        # simply instantiate the class, as all instances of this class are the same object.
        self.thread.start()
        return self 
    
    def update(self):

        while not self.stopped:
            bgr = self.camera.capture_array()
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB) # I don't like any image processing happening in this module, might move
            self.frame = rgb

        self.camera.close()
        
            
    def read(self) -> cv2.Mat:
        return self.frame 
    
    def stop(self):
        print("Releasing camera resources... ", end="")
        self.stopped = True
        self.camera.stop()
        self.thread.join()
        print("DONE")

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

