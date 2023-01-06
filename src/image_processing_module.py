# imports
import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as mpatches
import math
import skimage
from skimage.util import img_as_float, crop
from skimage.measure import regionprops, label
from skimage.morphology import remove_small_objects
from PIL import Image
#import picamera
import time
import datetime

# function to modify image
def image_changer(img):
    print(img.shape)
    # crop to bottom half of image
    crop = img[int(img.shape[0] / 2) : int(img.shape[0]), 0 : int(img.shape[1])].copy()
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (45, 45), 0)
    ret, binary = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)
    float = img_as_float(binary)
    labelFloat = label(float)
    filtered = remove_small_objects(labelFloat, 16000, 1)
    return filtered


def measure_angles(img):
    degrees = []
    for region in regionprops(img):
        majorAxisDegree = region.orientation * (180 / np.pi) + 90
        """print(
            "Angle: "
            + str(majorAxisDegree)
            + " Lengths: "
            + str(region.axis_minor_length)
            + ", "
            + str(region.axis_major_length)
        )"""
        degrees.append(majorAxisDegree)
    return degrees


def steering_output(angles):
    if len(angles) == 2:
        return((180 - (angles[0]+angles[1]))/180)
    elif len(angles) == 1:
        if angles[0] >= 5:
            return ((180-angles[0])/180)
        else:
            #throw stop flag as end has been reached
            pass

def plot_lines(img):
    for region in regionprops(img):
        minr, minc, maxr, maxc = region.bbox
        rect = mpatches.Rectangle(
            (minc, minr),
            maxc - minc,
            maxr - minr,
            fill=False,
            edgecolor="red",
            linewidth=2,
        )
        y0, x0 = region.centroid
        orientation = region.orientation
        x1 = x0 + math.cos(orientation) * 0.5 * region.axis_minor_length
        y1 = y0 - math.sin(orientation) * 0.5 * region.axis_minor_length
        x2 = x0 - math.sin(orientation) * 0.5 * region.axis_major_length
        y2 = y0 - math.cos(orientation) * 0.5 * region.axis_major_length
        # plt.add_patch(rect)
        plt.plot((x0, x1), (y0, y1), "-r", linewidth=2)
        plt.plot(x0, y0, ".g", markersize=5)
        bx = (minc, maxc, maxc, minc, minc)
        by = (minr, minr, maxr, maxr, minr)
        plt.plot(bx, by, "-b", linewidth=2)
    return img


# test image processing on image from camera
def take_picture():
    with picamera.PiCamera() as camera:
        """
        camera.resolution = (320, 240)
        camera.framerate = 24
        time.sleep(2)
        image = np.empty((240 * 320 * 3,), dtype=np.uint8)
        camera.capture(image, "bgr")
        image = image.reshape((240, 320, 3))
        """
        date = datetime.datetime.now().strftime("%m_%d_%Y-%I_%M_%S%p")
        camera.capture(f"captures/snapshot_{date}.jpg", format="jpeg")
        image = mpimg.imread(f"captures/snapshot_{date}.jpg")
        os.remove(f"captures/snapshot_{date}.jpg")
        return image


def processing_test():
    # initialize folder
    folder_dir = "test/assets"
    # initialize image name array
    names = []
    for image in os.listdir(folder_dir):
        names.append(image)
    # initialize image files array
    files = []
    for name in names:
        image = mpimg.imread(folder_dir + "/" + name)
        files.append(image)
    # initialize plot
    fig = plt.figure(figsize=(10, 7))
    rows = 3
    columns = 4
    # display initial images
    for i in range(len(names)):
        fig.add_subplot(rows, columns, i + 1)
        plt.imshow(files[i])
        plt.axis("off")
        plt.title(names[i])
    finalFig = plt.figure(figsize=(10, 7))
    finalArray = []
    for name in names:
        image = mpimg.imread(folder_dir + "/" + name)
        finalArray.append(image_changer(image))
    for i in range(len(finalArray)):
        finalFig.add_subplot(rows, columns, i + 1)
        plt.imshow(finalArray[i])
        print(names[i], measure_angles(finalArray[i]), steering_output(measure_angles(finalArray[i])))
        plt.axis("off")
        plt.title(names[i])
    plt.show()


if __name__ == "__main__":
    processing_test()
    # take_picture()
