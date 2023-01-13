import picamera
import time
import numpy as np
import cv2
import io
from io import BytesIO
from matplotlib import pyplot as plt


class Camera:
    def __init__(self):
        self.camera = picamera.PiCamera(resolution="VGA")
        self.camera.framerate = 60
        self.stream = io.BytesIO()
        self.camera.start_preview(alpha=10)

    def capture(self):
        self.camera.capture(self.stream, "png", use_video_port=True)
        array = cv2.imdecode(np.frombuffer(self.stream.getvalue(), dtype=np.uint8), 1)
        return array

    def stop(self):
        self.camera.stop_preview()
