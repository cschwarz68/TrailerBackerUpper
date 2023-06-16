"""
Streaming to web server.
"""

from flask import Flask
import numpy as np
import cv2

# Package Imports
from image_processing_module import zero_image

class Streamer:
    """
    Streaming to web server.
    """

    def __init__(self) -> Flask:
        self.app = Flask(__name__)

    def gen_frames(self, image: cv2.Mat):
        print("Streaming.")

        while True:
            if image is None:
                image_copy = np.zeros((10 ,10 ,3), np.uint8)
            else:
                image_copy = image.copy()
            buffer = cv2.imencode('.jpg', image_copy)[1]
            frame = buffer.tobytes()
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n") # Concatenate frame one by one and show result.
