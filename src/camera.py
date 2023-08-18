# Support for the `picamera` moudle has ended. `picamera2` aims to replace it using the new libcamera system
# Unfortunately, `picamera2` is in very early stages of development. It does seem to be quite slow, but that might just be my fault
# for coding poorly. In any case, the interface for controlling the camera's settings is very confusing.
# Please consult https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf before making any crazy changes in this module.

"""
This module provides an interface to the Raspberry Pi Camera via the Camera class.
"""

from picamera2 import Picamera2
from threading import Thread 
import libcamera
import cv2

import time

from constants import CameraSettings


class Camera:
    """
    Camera acts encapsulates the onboard camera of the Raspberry Pi. The camera can operate in both blocking and non-blocking modes. See Camera.start()
    """
     
    _self = None
    camera = None

    def __new__(cls):
        # Ensures only one instance of Camera exists at one time. Any module creating a camera object references the SAME camera. This is very useful.
        # Once second camera is set up I will make two children of this class (one for each camera), and those classes will be singletons.
        if cls._self is None:
            cls._self = super().__new__(cls)

        return cls._self
   
    def __init__(self):
        """
        Constructs a camera object. Framerate and resolution will be set according to values in the project's config.yml file.
        """
        if self.camera is None:
            self.camera = Picamera2()
            self.thread = Thread(target=self._update, args = ())

        if not self.camera.started:
            resolution = CameraSettings.RESOLUTION
            self.config = self.camera.create_video_configuration(main= {"size":resolution})
            self.config["transform"] = libcamera.Transform(hflip=True,vflip=True) # 180 degree rotation since the camera is upside-down.
            self.camera.configure(self.config)

        

        self.camera.start()

        time.sleep(2) # Needs a moment to get ready; doucmentations says to do this.
        self.camera.set_controls({"AeEnable": True, "AwbEnable": True, "FrameRate": CameraSettings.FRAMERATE})

      
        # See page 69 (ha) of https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf for more camera control information
        # (Appendix C: Camera controls)

        bgr= self.camera.capture_array() # initialize camera with non-None frame
        self.frame = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB) # change to RGB color scheme
        self.stopped = False
    
    def start(self):
        """
        This method starts a thread for camera updating. See `Camera.update()`
        """
        self.thread.start()
        return self 
    
    def _update(self):
        """
        This method is the target of `Camera.thread`. While the thread is active, the camera will continuosly read frames.
        `Camera.frame` will always be the latest frame captured.
        """
        while not self.stopped:
            bgr = self.camera.capture_array()
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB) # I don't like any image processing happening in this module, might move
            self.frame = rgb

        self.camera.close()
        
            
    def read(self) -> cv2.Mat:
        """
        This method is the outside interface for reading the frame from the camera. If the camera thread has been started, this method will return the
        latest captured frame. If the camera is operating in the same thread as this method call, the function will block until a frame has been returned.
        """
        if not self.thread.is_alive():
            bgr = self.camera.capture_array()
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            self.frame = rgb
        return self.frame 
    
    def stop(self):
        """
        This function shuts down the camera and joins the camera thread, if it exists.
        """
        print("Releasing camera resources... ", end="")
        self.stopped = True
        self.camera.stop()
        if self.thread.is_alive():
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

