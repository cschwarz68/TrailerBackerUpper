# import the necessary packages
import picamera
from picamera.array import PiRGBArray
import time
import cv2

#initialize camera and filename
camera = picamera.PiCamera()
rawCapture = PiRGBArray(camera)
date = "%Y%m%d-%H%M"
filename = "pi_recording_"+date+".h264"
#main loop to save video
def camera_main():
    time.sleep(0.1)
    camera.resolution = (640, 480)
    camera.start_recording(filename)
    camera.wait_recording(60)
    camera.stop_recording()
#display video
time.sleep(0.1)
camera.capture(rawCapture, format="bgr")
image = rawCapture.array
cv2.imshow("Image", image)

if __name__ == "__main__":
    camera_main