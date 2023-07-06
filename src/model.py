"""
Neural Network Independent Module (Legacy)

Autonomous A.I. navigation.

IMPORTANT
This module's drivetrain code relies on legacy modules.
Remember to disable the gpio daemon, otherwise nothing will move.
"""

import time

# Package Imports
from keras.models import load_model
from picamera2 import Picamera2


# Local Imports
from car import Car
from camera import Camera
from motor import cleanup

model = load_model('/home/nads/Documents/Python/TrailerBackerUpper/src/NN/models/straight_line_driver.h5')
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
    car = Car()
    cam = Camera()

    end_time = time.time() + 80

    while time.time() < end_time:
        image = cam.capture()
        steer_angle = compute_steering_angle(image)
        car.set_steering_angle(steer_angle)
        car.set_drive_power(-.7)

    car.set_drive_power(0)
    car.set_steering_angle(0)
    
    cam.stop()
    cleanup()
