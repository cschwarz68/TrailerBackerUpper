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
from PIL import Image as im
#import picamera
import time
import datetime


def capture_test():
    folder_dir = "captures"
    for name in os.listdir(folder_dir):
        string = folder_dir+"/"+name
        array = np.fromstring(string)
        print(array.shape)


# function to modify image
def image_changer(img):
    # crop to bottom half of image
    crop = img[int(img.shape[0] / 2) : int(img.shape[0]), 0 : int(img.shape[1])]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    print(f"max value of gray is {max(gray[0])}")
    thresh = int(max(gray[0])*0.8)
    # thresh = 150
    blur = cv2.GaussianBlur(gray, (21,21), 0)
    ret, binary = cv2.threshold(blur, thresh, 255, cv2.THRESH_BINARY)
    float = img_as_float(binary)
    labelFloat = label(float)
    filtered = remove_small_objects(labelFloat, 1600, 1)
    return filtered


def edge_detector(img):
    #img = cv2.imread("test/assets/ropes.jpg")
    #crop = img[int(img.shape[0] / 2) : int(img.shape[0]), 0 : int(img.shape[1])]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = int(max(gray[0])*0.8)
    blur = cv2.GaussianBlur(gray, (21,21), 0)
    ret, binary = cv2.threshold(blur, thresh, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(binary, 200, 400)
    return edges


def region_of_interest(edges):
    height, width = edges.shape
    mask = np.zeros_like(edges)

    # only focus bottom half of the screen
    polygon = np.array([[
        (0, height * 1 / 2),
        (width, height * 1 / 2),
        (width, height),
        (0, height),
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)
    return cropped_edges


def detect_line_segments(img):
    rho = 1  # distance precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
    min_threshold = 10  # minimal of votes
    line_segments = cv2.HoughLinesP(img, rho, angle, min_threshold, 
                                    np.array([]), minLineLength=8, maxLineGap=4)
    return line_segments
    
def average_slope_intercept(frame, line_segments):
    lane_lines = []
    if line_segments is None:
        print("no lines")

    height, width, _ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
    right_region_boundary = width * boundary # right lane line segment should be on left 2/3 of the screen

    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))
        
    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))
    
    return lane_lines


def make_points(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

    # bound the coordinates within the frame
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]


def display_lines(frame, lines, line_color=(0, 255, 0), line_width=2):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image

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
    normalized_output = 0
    if len(angles) == 2:
        normalized_output = (180 - (angles[0] + angles[1])) / 180
    elif len(angles) == 1:
        if angles[0] >= 5:
            normalized_output = (180 - angles[0]) / 180
        else:
            # throw stop flag as end has been reached
            pass
    return normalized_output


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
        img.add_patch(rect)
        plt.plot((x0, x1), (y0, y1), "-r", linewidth=2)
        plt.plot(x0, y0, ".g", markersize=5)
        bx = (minc, maxc, maxc, minc, minc)
        by = (minr, minr, maxr, maxr, minr)
        plt.plot(bx, by, "-b", linewidth=2)
    return img


def plot_cv2_lines(img):
    pass

def plot_test():
    image = cv2.imread("test/assets/ropes.jpg")
    image = cv2.resize(image, (640, 480))
    edges = edge_detector(image)
    cropped_edges = region_of_interest(edges)
    line_segments = detect_line_segments(cropped_edges)
    lane_lines = average_slope_intercept(image, line_segments)
    line_image = display_lines(image, lane_lines)
    plt.imshow(line_image)
    plt.show()


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
        print(
            names[i],
            measure_angles(finalArray[i]),
            steering_output(measure_angles(finalArray[i])),
        )
        plt.axis("off")
        plt.title(names[i])
    plt.show()


if __name__ == "__main__":
    #processing_test()
    # take_picture()
    # capture_test()
    plot_test()
