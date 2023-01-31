# import the necessary packages
import cv2
import numpy as np
import picamera
from picamera.array import PiRGBArray
import time
import image_processing_module as ip
from matplotlib import pyplot as plt
import timeit
from pathlib import Path

print(cv2.__version__)

# camera = picamera.PiCamera()


class Camera:
    def __init__(self):
        # initialize camera and filename
        self.camera = picamera.PiCamera(resolution=(640, 480))

        # capture without warmup

    def quick_capture(self):
        image = np.empty((480, 640, 3,), dtype=np.uint8)
        self.camera.capture(image, "bgr")
        return image

    def stop(self):
        self.camera.stop_preview()
        self.camera.close()


# main loop to save video
def image_test():
    camera = picamera.PiCamera(resolution=(640, 480))
    camera.resolution = (1024, 768)
    camera.start_preview()
    # Camera warm-up time
    time.sleep(2)

    # basic capture
    p = Path("../captures")
    file = p / "image.jpg"
    file = "image.jpg"
    # camera.capture(str(file))

    # using raw array
    # rawCapture = PiRGBArray(camera)
    # camera.capture(rawCapture, format="bgr")
    # image = rawCapture.array
    # image = ip.image_changer(image)
    # cv2.imshow("Image", image)

    # using
    camera.resolution = (640, 480)
    camera.framerate = 60
    image = np.empty((640 * 480 * 3,), dtype=np.uint8)
    camera.capture(image, "bgr")
    camera.stop_preview()
    camera.close()
    image = image.reshape((480, 640, 3))
    image = ip.image_changer(image)
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("Image2", image)
    # plt.imshow(image)
    # plt.show()


def video_test():
    camera = picamera.PiCamera(resolution=(640, 480))
    date = "%Y%m%d-%H%M"
    filename = "pi_recording_" + date + ".h264"
    camera.resolution = (640, 480)
    camera.start_recording(filename)
    camera.wait_recording(30)
    camera.stop_recording()
    camera.close()


def preview_test():
    camera = picamera.PiCamera(resolution=(640, 480))
    camera.start_preview(alpha=200)
    time.sleep(5)
    camera.stop_preview()
    camera.close()


# compute binary search time
def image_time():
    SETUP_CODE = """
from __main__ import image_test
from random import randint"""

    TEST_CODE = """
image_test()"""

    # timeit.repeat statement
    times = timeit.timeit(setup=SETUP_CODE, stmt=TEST_CODE, number=1)

    # printing minimum exec. time
    print("Image test time: {}".format(times))


if __name__ == "__main__":
    print("image test")

    image_time()
    # image_test()

    print("preview test")
    preview_test()
    time.sleep(10)
