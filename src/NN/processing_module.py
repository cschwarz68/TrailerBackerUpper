# imports
from picamera2 import Picamera2
import cv2
import numpy as np
import math
import time
# from matplotlib import pyplot as plt
import archive.steer_module as sr
import archive.drive_module as dr
from keras.models import load_model
import quick_capture_module as qc

model = load_model('models/lane_navigation_final_2.h5')


def img_preprocess(image):
    # print(image.shape)
    image = image[int(image.shape[0] / 2) : int(image.shape[0]), 0 : int(image.shape[1])]  # remove top half of the image, as it is not relavant for lane following
    # print(image.shape)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)  # Nvidia model said it is best to use YUV color space
    image = cv2.GaussianBlur(image, (3,3), 0)
    image = cv2.resize(image, (200,66)) # input image size (200,66) Nvidia model
    image = image / 255 # normalizing, the processed image becomes black for some reason.  do we need this?
    return image
        
def compute_steering_angle(frame):
    preprocessed = img_preprocess(frame)
    X = np.asarray([preprocessed])
    #print(type(X))
    steering_angle = model.predict(X)[0]
    return steering_angle 

def image_loop():
    steer = sr.Steer()
    drive = dr.Drive()
    camera = qc.StreamCamera()
    

    while True:
        image = camera.capture()
        steer_angle = compute_steering_angle(image)
        steer.steer_by_angle(steer_angle)
        drive.drive(.7)
    camera.stop()

if __name__ == "__main__":
    image_loop()

