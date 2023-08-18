"""
Autonomous A.I. navigation module.

This is legacy code (updated to use pigpiod insted of RPi.GPIO, but that's it).

I will maybe eventually document how to supply training frames to Google Colab as well as document the functionality of this module.

Neural Network is once again being put aside, this time because of colabs requirements to be present while connected to one of their remote runtimes.
It can take many hours to train from a couple minutes of video, so actually sitting and waiting for it isn't very fun.

I would train it on the pc that I do my work on, but they stole my graphics card to use in someone else's pc!!!! Those monsters!!!!
Don't they know this robot is the most important thing we do in this office???
"""

import time

# Package Imports
from keras.models import load_model
import numpy as np
import cv2


# Local Imports
from NN.src.camera_single_threaded import Camera # This module has not been updated to use multi-threaded camera
from truck import Truck

model = load_model('./src/NN/models/straight_line_driver.h5')
print("model loaded")

def img_preprocess(image: cv2.Mat) -> cv2.Mat:
    # Remove top half of the image, as it is not relavant for lane following.
    # image = image[int(image.shape[0] / 2) : int(image.shape[0]), 0 : int(image.shape[1])]
    # Nvidia model said it's best to use the YUV color space.
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    image = cv2.GaussianBlur(image, (3, 3), 0)
    image = cv2.resize(image, (200, 66))
    # Normalizing, the processed image becomes black.
    """
    The original comment here expressed confusion as to the purpose of normalizing the output.

    Hypothesis:
        "The YUV model defines one luminance component (Y) meaning physical linear-space brightness, 
         and two chrominance components, called U (blue projection) and V (red projection) respectively."

        By dividing all elements in the image matrix by the maximum value 255, the luminance is normalized to a percentage.
        This may be useful in neural networks, as it's more common (citation needed) for the inputs to be from 
        0 - 1. Though it may not matter, as the original comment also expressed.
    """
    image = image / 255
    return image

def compute_steering_angle(frame: cv2.Mat):
    preprocessed = img_preprocess(frame)
    X = np.asarray([preprocessed])
    steering_angle = model.predict(X)[0]
    return steering_angle

if __name__ == "__main__":
    truck = Truck()
    cam = Camera()

    end_time = time.time() + 80

    while time.time() < end_time:
        image = cam.read()
        steer_angle = compute_steering_angle(image)
        truck.set_steering_angle(steer_angle)
        truck.set_drive_power(-.7)

    truck.set_drive_power(0)
    truck.set_steering_angle(0)
    
    cam.stop()
    truck.cleanup()
