import picamera
import time
import numpy as np
import cv2
import io
from io import BytesIO
from matplotlib import pyplot as plt
import image_processing_module as ip


class StreamCamera:
    def __init__(self):
        self.camera = picamera.PiCamera(resolution=(640, 480))
        self.camera.framerate = 60

        self.camera.start_preview(alpha=10)

    def capture(self):
        stream = io.BytesIO()
        self.camera.capture(stream, "png", use_video_port=True)

        array = cv2.imdecode(np.frombuffer(stream.getvalue(), dtype=np.uint8), 1)
        np.save("test4", array)
        return array

    def stop(self):
        self.camera.stop_preview()


if __name__ == "__main__":
    camera = StreamCamera()
    plt.imshow(camera.capture())
    plt.show()
