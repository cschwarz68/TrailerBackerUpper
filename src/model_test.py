from keras.models import load_model
import quick_capture_module as qc
import cv2
import numpy as np

model = load_model('models/lane_navigation_final.h5')

video_directory = "test_captures"
video_file = video_directory + "/video_test"

cap = cv2.VideoCapture(video_file + ".h264")

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

try:
    i = 0
    while cap.isOpened():
        _, frame = cap.read() 
        angle = compute_steering_angle(frame)
        print(angle)
finally:
        cap.release()
        cv2.destroyAllWindows()