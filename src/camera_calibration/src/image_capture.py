import numpy as np
import glob
import cv2
import sys
sys.path.insert(0,"./src/") # gamepad and camera are located in parent directory
from gamepad import Gamepad, Inputs
from camera import Camera

# This module captures images from the camera when A is pressed on the controller.
# Images are saved to '.src/camera_calibration_calibration_images'
# The inteneded use of this module is to capture images for fisheye-correction calibration, but you could just use it to take pictures.


if __name__ == "__main__":
    cam = Camera() # not threaded
    g = Gamepad()

    


    filepath = "./src/camera_calibration/calibration_images/"
    image_num = ord('a')
    print("STARTED")
    while True:
        g.update_input()

        if g.was_pressed(Inputs.A):
            img = cam.read()
            
            filename = "sample_image_"+chr(image_num)+".jpg"
            
            cv2.imwrite(filepath + filename, img)
            print("Saved file:", filepath + filename)

            image_num += 1
        elif g.was_pressed(Inputs.B):
            break

    cam.stop()



