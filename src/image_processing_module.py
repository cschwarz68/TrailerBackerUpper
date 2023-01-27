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


def compute_steering_angle(frame, lane_lines):

    if len(lane_lines) == 0:
        return -90

    height, width = frame.shape[0], frame.shape[1]
    if len(lane_lines) == 1:
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
    else:
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        camera_mid_offset_percent = 0.02 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
        mid = int(width / 2 * (1 + camera_mid_offset_percent))
        x_offset = (left_x2 + right_x2) / 2 - mid

    # find the steering angle, which is angle between navigation direction to end of center line
    y_offset = int(height / 2)

    angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
    steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel
    return steering_angle

def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5, ):
    heading_image = np.zeros_like(frame)
    height, width = frame.shape[0], frame.shape[1]
    steering_angle_radian = steering_angle / 180.0 * math.pi
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)

    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image
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


def plot_test():
    image = cv2.imread("test/assets/ropes.jpg")
    image = cv2.resize(image, (640, 480))
    edges = edge_detector(image)
    cropped_edges = region_of_interest(edges)
    line_segments = detect_line_segments(cropped_edges)
    lane_lines = average_slope_intercept(image, line_segments)
    line_image = display_lines(image, lane_lines)
    steering_angle = compute_steering_angle(line_image, lane_lines)
    steering_image = display_heading_line(line_image, steering_angle)
    plt.imshow(steering_image)
    plt.show()


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
    plot_test()
