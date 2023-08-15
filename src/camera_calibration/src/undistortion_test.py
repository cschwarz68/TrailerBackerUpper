import numpy as np
import glob
import cv2
import sys
sys.path.insert(0,"./src/") # gamepad and camera are located in parent directory
from gamepad import Gamepad, Inputs
from camera import Camera

# This module reads camera matrix and distortion coefficients from src/calibrations/, captures images, applies undistortion to them, and saves the images to src/corrected_images/

if __name__ == "__main__":
    cam = Camera() # not threaded
    g = Gamepad()

    

    filepath = "./src/camera_calibration/"
    output_dir = filepath+"corrected_images/"
    input_dir = filepath+"calibrations/"
    image_num = ord('a')
    print("STARTED")
    while True:
        g.update_input()

        if g.was_pressed(Inputs.A):
            img = cam.read()
            matrix = np.load(input_dir+"matrix.npz")['arr_0']
            

            distortion = np.load(input_dir+"distortion.npz")['arr_0']

            h, w = img.shape[:2]
	
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(matrix, distortion, (w,h), 1, (w,h))
            dst = cv2.undistort(img, matrix, distortion, None, newcameramtx)
            x,y,w,h = roi
            
            dst = dst[y:y+h, x:x+w]
            
            filename = "undistorted_image_"+chr(image_num)+".jpg"
            cv2.imwrite(output_dir+ filename, dst)
            print("Saved file:", output_dir + filename)

            image_num += 1
        elif g.was_pressed(Inputs.B):
            break

    cam.stop()