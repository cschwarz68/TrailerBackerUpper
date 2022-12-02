# import the necessary packages
import picamera
from picamera.array import PiRGBArray
import cv2

print(cv2.__version__)

# initialize camera and filename
camera = picamera.PiCamera()
rawCapture = PiRGBArray(camera)
date = "%Y%m%d-%H%M"
filename = "pi_recording_" + date + ".h264"

# main loop to save video
def image_test():
    # display image
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    cv2.imshow("Image", image)


def video_test():
    camera.resolution = (640, 480)
    camera.start_recording(filename)
    camera.wait_recording(60)
    camera.stop_recording()


if __name__ == "__main__":
    image_test()
