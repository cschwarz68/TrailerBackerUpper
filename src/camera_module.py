# import the necessary packages
import cv2
import numpy as np
import picamera
from picamera.array import PiRGBArray
import time

print(cv2.__version__)

# initialize camera and filename
camera = picamera.PiCamera()


# main loop to save video
def image_test(p):
    camera.resolution = (1024, 768)
    # camera.start_preview()
    # Camera warm-up time
    time.sleep(2)

    # basic capture
    file = p / "image.jpg"
    camera.capture(str(file))

    # using raw array
    rawCapture = PiRGBArray(camera)
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    cv2.imshow("Image", image)

    # using
    camera.resolution = (640, 480)
    camera.framerate = 60
    image = np.empty((640 * 480 * 3,), dtype=np.uint8)
    camera.capture(image, "bgr")
    image = image.reshape((480, 640, 3))
    cv2.imshow("Image2", image)

    # camera.stop_preview()


def video_test():
    date = "%Y%m%d-%H%M"
    filename = "pi_recording_" + date + ".h264"
    camera.resolution = (640, 480)
    camera.start_recording(filename)
    camera.wait_recording(30)
    camera.stop_recording()


def preview_test():
    camera.start_preview(alpha=200)
    time.sleep(30)
    camera.stop_preview()


if __name__ == "__main__":
    from pathlib import Path

    p = Path("../media")

    print("image test")
    image_test(p)

    print("preview test")
    preview_test()
    time.sleep(10)
