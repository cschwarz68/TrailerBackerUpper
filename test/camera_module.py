# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

# initialize the camera
camera = PiCamera()

# allow the camera to warmup
time.sleep(0.1)

def camera_main():
    # grab a reference to the raw camera capture
    rawCapture = PiRGBArray(camera)
    # grab an image from the camera
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    # display the image on screen and wait for a keypress
    cv2.imshow("Image", image)
    cv2.waitKey(0)

if __name__ == "__main__":
    camera_main