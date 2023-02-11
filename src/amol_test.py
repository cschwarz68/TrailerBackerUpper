import picamera
import time
import numpy as np
import cv2
import io
import os
from io import BytesIO
from matplotlib import pyplot as plt
import image_processing_module as ip


class StreamCamera:
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.framerate = 60

        self.camera.start_preview(alpha=20)

    def capture(self):
        stream = io.BytesIO()
        self.camera.capture(stream, "png", use_video_port=True)

        array = (cv2.imdecode(np.frombuffer(stream.getvalue()), dtype=np.uint8), 1)
        # np.save("test4", array)
        return array

    def stop(self):
        self.camera.stop_preview()
        self.camera.close()


if __name__ == "__main__":
    directory = "test_captures"

    camera = StreamCamera()

    for i in range(10):
        image = camera.capture()
        filepath = os.path.join(directory, "test_{}.jpeg".format(i))
        cv2.imwrite(filepath, image)
    # plt.imshow(camera.capture())
    # camera.close()
    # plt.show()
    camera.test()
