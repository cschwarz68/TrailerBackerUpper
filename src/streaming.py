from flask import Flask
import cv2

class Streamer:
    """
    Streaming to web server.
    """

    def __init__(self) -> Flask:
        self.app = Flask(__name__)

    def gen_frames(self, image: cv2.Mat):
        base_height, base_width, _ = image.shape
        print(f"Streaming with dimensions {base_width}x{base_height}.")

        while True:
            image = cv2.resize(image, (base_width, base_height))
            buffer = cv2.imencode('.jpg',image)[1]
            frame = buffer.tobytes()
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n") # Concatenate frame one by one and show result.
