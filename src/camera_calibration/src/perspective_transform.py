import numpy as np
import glob
import cv2
import sys
sys.path.insert(0,"./src/") # gamepad and camera are located in parent directory
from gamepad import Gamepad, Inputs
from camera import Camera
import image_utils as iu

# This module captures images from the camera when A is pressed on the controller.
# Images are saved to '.src/camera_calibration_calibration_images'
# The inteneded use of this module is to capture images for fisheye-correction calibration, but you could just use it to take pictures.


if __name__ == "__main__":
    cam = Camera() # not threaded
    g = Gamepad()

    


    filepath = "./src/camera_calibration/"
    output = "transformation_images/"
    calibrations = "calibrations/"
    image_num = ord('a')
    print("STARTED")
    start_img = cam.read()

    camera_matrix =  np.load(filepath+calibrations+"matrix1600x1200.npz")['arr_0']
    distortion_coefficients = np.load(filepath+calibrations+"distortion1600x1200.npz")['arr_0']
    h, w = start_img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coefficients, (w,h), 1, (w,h))
    image_remap_x, image_remap_y = cv2.initUndistortRectifyMap(camera_matrix, distortion_coefficients, None, newcameramtx, (w,h), 5)


    undistorted = iu.undistort(start_img, image_remap_x, image_remap_y, roi)

    height, width, _ = undistorted.shape

    tl = [width *2/9, height * 1/4]
    tr = [width * 7/9, height * 1/4]
    bl = [0, height* 3/4]
    br = [width, height* 3/4]


    src = np.float32([tl, tr, bl, br])

    tl = [0,0]
    tr = [start_img.shape[1], 0]
    bl = [0, start_img.shape[0]]
    br = [start_img.shape[1], start_img.shape[0]]

    dst = np.float32([tl, tr, bl, br])

    matrix = cv2.getPerspectiveTransform(src, dst)

    while True:
        g.update_input()

        if g.was_pressed(Inputs.A):
            img = cam.read()
            undistorted = iu.undistort(img, image_remap_x, image_remap_y, roi)

            
            filename = "transformed_image_"+chr(image_num)+".jpg"

            res = cv2.warpPerspective(undistorted, matrix, (start_img.shape[1], start_img.shape[0]) )
            
            cv2.imwrite(filepath + output+ filename, res)
            print("Saved file:", filepath + output +  filename)

            image_num += 1
        elif g.was_pressed(Inputs.B):
            break

    cam.stop()

