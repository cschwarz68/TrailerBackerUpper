import picamera2
from picamera2 import Picamera2, Preview
from libcamera import Transform
#import picamera2.array
import time
import numpy as np
import cv2
import io
from io import BytesIO
#from matplotlib import pyplot as plt
import image_processing_module as ip

import numpy as np


class StreamCamera:
    def __init__(self):
        self.camera = Picamera2()

        # self.camera.preview_configuration.main.format = "YUV420"
        self.camera.start()
        time.sleep(1)
        # self.camera.resolution = (640, 480)
        # self.camera.framerate = 60

        # self.camera.start_preview(alpha=20)

    def capture(self):
        array = self.camera.capture_array()
        array=np.rot90(array,2)
        array = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
        return array

    def test(self):
        self.camera.capture("test_image.png", format="bgr", use_video_port=True)
        self.camera.stop()

    def stream_capture(self):
        with picamera2.array.PiRGBArray(self.camera) as stream:
            self.camera.capture(stream, format="bgr", use_video_port=True)
            image = stream.array

            image = cv2.flip(image,-1)
            print(image.shape)
        return image

    def stop(self):
        self.camera.stop_preview()
        self.camera.close()


if __name__ == "__main__":
    camera = StreamCamera()


    while True:
        #print('image?')
        image = camera.capture()
        #print('image?')
        image = ip.get_reds(image)
        image = ip.get_angle_image(image)
        cv2.imshow("img", image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    camera.stop()
