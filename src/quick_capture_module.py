import picamera
import picamera.array
import time
import numpy as np
import cv2
import io
from io import BytesIO
from matplotlib import pyplot as plt
import image_processing_module as ip

import numpy as np


class StreamCamera:
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 60

        self.camera.start_preview(alpha=20)

    def capture(self):
        stream = io.BytesIO()
        self.camera.capture(stream, "png", use_video_port=True)

        array = cv2.imdecode(np.frombuffer(stream.getvalue(), dtype=np.uint8), 1)
        # np.save("test4", array)
        return array

    def test(self):
        self.camera.capture("test_image.png", format="bgr", use_video_port=True)
        self.camera.stop()

    def stream_capture(self):
        with picamera.array.PiRGBArray(self.camera) as stream:
            self.camera.capture(stream, format="bgr", use_video_port=True)
            image = stream.array
        return image

    def stop(self):
        self.camera.stop_preview()
        self.camera.close()


def preview_test():
    with picamera.PiCamera() as camera:
        camera.start_preview(alpha=5)
        camera.resolution = (640, 480)
        time.sleep(2)
        with picamera.array.PiRGBArray(camera) as stream:
            camera.capture(stream, format="bgr")
            image = stream.array
            cv2.imshow("img", image)
            cv2.waitKey()


if __name__ == "__main__":
    camera = StreamCamera()
    while True:
        image = camera.stream_capture()
        cv2.imshow("img", image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
