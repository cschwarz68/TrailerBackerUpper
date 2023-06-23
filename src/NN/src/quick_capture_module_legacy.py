"""
IMPORTANT

Restored legacy code. Not refactored. For neural network only.
"""

'''
GENERAL SUMMARY
This is a Python script that uses the Raspberry Pi camera module (specifically the picamera2 library) to capture and process images in real-time. 
It defines a StreamCamera class that initializes and controls the camera. 
The capture method captures an image from the camera and returns a numpy array representing the image, after rotating and converting it to RGB format. 
The stream_capture method is similar, but captures and returns a continuous stream of images. The test method captures a single image and saves it to disk.

The main script creates an instance of the StreamCamera class, captures an image in a loop, applies some image processing techniques from an external module 
(image_processing_module), displays the resulting image using the OpenCV library, and exits when the 'q' key is pressed. Finally, it calls the stop method to stop the 
camera preview and close the camera.

ANYTHING WITH TABS ARE COMMENTS THAT MIGHT BE HELPFUL FOR FUTURE EXPANSION OF THE MODULE
'''

#imports
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
# import image_processing_module as ip
import numpy as np

#initialize the StreamCamera class
class StreamCamera:
    def __init__(self):
        #initialize Picamera2 to self.camera
        self.camera = Picamera2()
            # self.camera.preview_configuration.main.format = "YUV420"
        self.camera.start()
        time.sleep(1)
            # self.camera.resolution = (640, 480)
            # self.camera.framerate = 60
            # self.camera.start_preview(alpha=20)

    #method to take an image input and applies a 90 degree rotation twice and color change from BGR to RGB
    def capture(self):
        array = self.camera.capture_array()
        array=np.rot90(array,2)
        array = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
        return array

    #method tests if the camera is working by taking an image and saving it to test_image.png
    def test(self):
        self.camera.capture("test_image.png", format="bgr", use_video_port=True)
        self.camera.stop()

    #method captures and returns an array in BGR format
    def stream_capture(self):
        with picamera2.array.PiRGBArray(self.camera) as stream:
            self.camera.capture(stream, format="bgr", use_video_port=True)
            image = stream.array

            image = cv2.flip(image,-1)
                # print(image.shape)
        return image

    #method to stop the camera
    def stop(self):
        self.camera.stop_preview()
        self.camera.close()

# #main method
# if __name__ == "__main__":
#     #initialize the camera
#     camera = StreamCamera()

#     #while loop to continuously capture images
#     while True:
#             #print('image?')
#         #captures an image
#         image = camera.capture()
#             #print('image?')
#         #method in image_proccessing
#         image = ip.display_reds_and_lane(image)
#             # image = ip.get_reds(image)
#             # image = ip.get_angle_image(image)
#         cv2.imshow("img", image)
#         #
#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break
#     camera.stop()
