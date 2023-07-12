"""
Neural Network Test Module (Legacy)

Reads a video and prints the predicted steering angles.
"""

# Package Imports
from keras.models import load_model
import numpy as np
from camera import Camera
import cv2

model = load_model('/home/nads2/TrailerBackerUpper/src/NN/models/lane_navigation_final_2.h5')

video_directory = "/home/nads2/TrailerBackerUpper/src/NN/nn_captures"



def img_preprocess(image: cv2.Mat) -> cv2.Mat:
    # Remove top half of the image, as it is not relavant for lane following.
    image = image[int(image.shape[0] / 2) : int(image.shape[0]), 0 : int(image.shape[1])]
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
    stream = Camera()

    try:
        i = 0
        while True:
            _, frame = stream.capture() 
            angle = compute_steering_angle(frame)-90
            print(angle)
    finally:
        pass
        #stream.release()
