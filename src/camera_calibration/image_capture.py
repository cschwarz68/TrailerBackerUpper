import numpy as np
import glob
import cv2
import sys
sys.path.insert(0,"./src/") # gamepad and camera are located in parent directory
from gamepad import Gamepad, Inputs
from camera import Camera



if __name__ == "__main__":
    cam = Camera() # not threaded
    g = Gamepad()

    


    filepath = "./src/camera_calibration/"
    image_num = 0
    print("STARTED")
    while True:
        g.update_input()

        if g.was_pressed(Inputs.A):
            img = cam.read()
            
            filename = "calibration_image"+str(image_num)+".jpg"
            cv2.imwrite(filepath+ filename, img)
            print("Saved file:", filepath + filename)

            image_num += 1
        elif g.was_pressed(Inputs.B):
            break

    cam.stop()



