"""
Processes images with OpenCV for autonomous navigation.

IMPORTANT

All images are represented by OpenCV matrices, which are aliases of numpy arrays.
"""

import math
import warnings

# Package Imports
import cv2
import numpy as np

# Local Imports
from constants import Lane_Bounds_Ratio, Drive_Params, Image_Processing_Calibrations

# Global Configuration
warnings.simplefilter('ignore', np.RankWarning)
# Ignoring Polyfit warning because it's bothersome.
# Supposedly we can resolve it by decreasing the order (third argument), but it's already at 1 here...

# Returns an image filtered for edges.
def edge_detector(img: cv2.Mat) -> cv2.Mat:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = int(max(gray[0]) * 0.8)
    blur = cv2.GaussianBlur(gray, (21, 21), 0)
    _, binary = cv2.threshold(blur, thresh, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(binary, 200, 400)
    return edges

# Crops an image to focus on the bottom half.
def region_of_interest(edges: cv2.Mat) -> cv2.Mat:
    height, width = edges.shape
    mask = np.zeros_like(edges)
    # Focus on bottom half.
    polygon = np.array(
        [
            [
                (0, height * 1 / 2), 
                (width, height * 1 / 2), 
                (width, height), 
                (0, height)
            ]
        ], 
        np.int32
    )
    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)
    return cropped_edges

# Detect lines segments with hough lines using cropped image filtered for edges.
# (x1, y1, x2, y2) - the coordinates for each line segment.
"""
IMPORTANT

Return an array of the form:
line_segments [
    [[x1, y1, x2, y2]], 
    [[x1, y1, x2, y2]], 
    [[x1, y1, x2, y2]], 
    [[x1, y1, x2, y2]], 
    ...
]

"Singleton" arrays.
"""
def detect_line_segments(img: cv2.Mat) -> np.ndarray:
    rho = 1             # Distance precision in pixels, i.e. 1 pixel.
    angle = np.pi / 180 # Angular precision in radians, i.e. 1 degree (radians = degrees * pi / 180).
    min_threshold = 10  # Minimal of votes for a line to be counted.
    line_segments = cv2.HoughLinesP(
        img, rho, angle, min_threshold, np.array([]), minLineLength=8, maxLineGap=4
    )
    return line_segments

# Extrapolates a line to its endpoints at the edges of the image. y is maxed at half the height.
# Used to determine deviation from lane.
def make_points(frame: cv2.Mat, line: np.ndarray) -> tuple[int, int, int, int]:
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height      # Bottom of the frame / image.
    y2 = int(y1 / 2) # Middle.

    # Extrapolate the line to a line segment with endpoints on the edges of the frame.
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return (x1, y1, x2, y2)

# Approximates the slope and intercept of each line segment, determines which side of the image it's on, 
# and then computes the average line for each side. Returns array of length 0 - 2 from `make_points`.
# The frame is the uncropped image.
def average_slope_intercept(frame: cv2.Mat, line_segments: np.ndarray) -> list[tuple[int, int, int, int]]:
    if line_segments is None:
        return []

    _, width, _ = frame.shape
    left_fit = []
    right_fit = []

    for line_segment in line_segments:
        x1, y1, x2, y2 = line_segment[0]
        fit = np.polyfit((x1, x2), (y1, y2), 1)
        slope, intercept = fit
        if ((slope < 0) and 
            (x1 < Lane_Bounds_Ratio.LEFT * width) and 
            (x2 < Lane_Bounds_Ratio.LEFT * width)):
            left_fit.append((slope, intercept))
        elif ((slope > 0) and 
              (x1 > Lane_Bounds_Ratio.RIGHT * width) and 
              (x2 > Lane_Bounds_Ratio.RIGHT * width)):
            right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0) # Get averages going downward. Collapse into one array.
    right_fit_average = np.average(right_fit, axis=0)
    lane_lines = []
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    return lane_lines

# Use lane lines to predict the steering angle in degrees.
# Arbitrary, maybe subject to change: 0 --> left, 90 --> straight, 180 --> right
def compute_steering_angle(frame: cv2.Mat, lane_lines: list[tuple[int, int, int, int]]) -> int:
    if len(lane_lines) == 0:
        # Continue straight if no lines are present...
        return Drive_Params.TURN_STRAIGHT

    height, width = frame.shape[0], frame.shape[1]
    if len(lane_lines) == 1:
        # In the event only a left lane or right lane was detected, 
        # we calculate the x-offset based on the difference between the extrapolated x coordinates.
        x1, _, x2, _ = lane_lines[0]
        x_offset = x2 - x1
    else:
        # Otherwise, the offset is based on the average between the topmost (as in the y-coordinate is at the middle of the frame) 
        # x-coordinates and the measured camera position. Note that the camera position may have to be recalibrated.
        _, _, left_x2, _ = lane_lines[0]
        _, _, right_x2, _ = lane_lines[1]
        mid = int(width / 2 * (1 + Image_Processing_Calibrations.CAMERA_MID_OFFSET_PERCENT))
        x_offset = (left_x2 + right_x2) / 2 - mid

    """
    IMPORTANT

    How the steering angle is calculated:
    
      Car Front
        /| --> angle_to_mid_radian
       / |                       |
      /  | }--> y_offset         V
     /   |                       Convert to degrees and add turn straight angle.
    /____|
   x_offset
    """
    y_offset = int(height / 2)
    angle_to_mid_radian = math.atan(x_offset / y_offset)
    angle_to_mid_deg = math.degrees(angle_to_mid_radian)
    steering_angle = int(angle_to_mid_deg + Drive_Params.TURN_STRAIGHT)
    return steering_angle

# Everything beneath this comment is for testing.

# Returns a black image with lines drawn on it.
def display_lines(frame: cv2.Mat, lines: list[tuple[int, int, int, int]], line_color=(255, 255, 255), line_width=2) -> cv2.Mat:
    line_image = np.zeros_like(frame) # Create black image with the same dimensions.
    if lines is None:
        return line_image
    for line in lines:
        x1, y1, x2, y2 = line
        cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    # Might be useful for overlaying the raw image.
    # line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image

# Makes a black image containing lane lines and the calculated path. 
def display_lanes_and_path(img: cv2.Mat):
    edges = edge_detector(img)
    cropped_edges = region_of_interest(edges)
    line_segments = detect_line_segments(cropped_edges)
    lane_lines = average_slope_intercept(img, line_segments)
    steering_angle_deg = compute_steering_angle(img, lane_lines)
    height, width = img.shape[0], img.shape[1]
    steering_angle_radian = math.radians(steering_angle_deg)
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)

    final_image = display_lines(img, lane_lines)
    cv2.line(final_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return final_image

# R
def lane_detection(img):
    """
    @brief plot lane lines and steering path on frame
    
    @param img(numpy array): A numpy array representation of original image
    
    @return final_image(numpy array): numpy array of img with lane lines and steering path plotted"""
    edges = edge_detector(img)
    cropped_edges = region_of_interest(edges)
    line_segments = detect_line_segments(cropped_edges)
    lane_lines = average_slope_intercept(img, line_segments)
    line_image = display_lines(img, lane_lines)
    steering_angle = compute_steering_angle(line_image, lane_lines)
    final_image = display_heading_line(line_image, steering_angle)
    return final_image

# Everything beneath this comment has not been refactored.

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


def get_steering_angle(img):
    """
    @brief get steering angle to keep car in middle of lane

    @param img(numpy array): A numpy array representation of original image

    @return steering_angle(int): steering angle to keep car in middle of lane
    """
    edges = edge_detector(img)
    cropped = region_of_interest(edges)
    line_segments = detect_line_segments(cropped)
    lane_lines = average_slope_intercept(img, line_segments)
    line_image = display_lines(img, lane_lines)
    steering_angle = compute_steering_angle(line_image, lane_lines)
    return steering_angle


def get_reds(img):
    """
    @brief filter image for red color to detect tape on trailer

    @param img(numpy array): A numpy array representation of image

    @return mask(Mat): image filtered for red
    """
    invert = ~img
    hsv = cv2.cvtColor(invert, cv2.COLOR_BGR2HSV)
    lower_cyan = np.array([80, 150, 40])
    upper_cyan = np.array([100, 255, 255])
    mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
    #res = cv2.bitwise_and(img, img, mask= mask)
    return mask


def get_angle_image(img):
    """
    @brief calculate angle of largest shape in image and calculate
    
    @param img(Mat): matrix representation of image
    
    @return image(array): image with angle of largest shape plotted"""
    contours = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    big_contour = max(contours, key=cv2.contourArea)
    M = cv2.moments(big_contour)
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"]) 
    origin_x, origin_y = int(img.shape[1]/2), img.shape[0]
    angle = math.atan2(origin_y - cy, origin_x - cx)
    angle = abs(math.floor(math.degrees(angle)))
    image = cv2.line(img, (origin_x, origin_y), (cx, cy), color=(255, 255, 255), thickness=5)
    image = cv2.putText(image, str(angle), (cx,cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,255), 2)
    return image


def get_red_angle(img):
    """
    @brief calculate angle of largest shape detected in image
    
    @param img(Mat): matrix representation of image
    
    @return angle(int): angle of shape"""
    contours = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    big_contour = max(contours, key=cv2.contourArea)
    M = cv2.moments(big_contour)
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"]) 
    origin_x, origin_y = int(img.shape[1]/2), img.shape[0]
    angle = math.atan2(origin_y - cy, origin_x - cx)
    angle = abs(math.floor(math.degrees(angle)))
    return angle


def display_reds_and_lane(img):
    """
    @brief detect and plot lane lines and line of red shape
    
    @param img(Mat): matrix representation of image
    
    @return line_image(numpy array): image with lane lines and red shape angle line
    """
    red = get_reds(img)
    # if no red detected use original image
    try:
        red_angle_image = get_angle_image(red)
    except:
        red_angle_image = img
    edges = edge_detector(img)
    cropped_edges = region_of_interest(edges)
    line_segments = detect_line_segments(cropped_edges)
    lane_lines = average_slope_intercept(img, line_segments)
    line_image = display_lines(red_angle_image, lane_lines)
    return line_image


def red_and_lane_angle(img):
    """
    @brief calculate and return angle of red shape and steering angle from lane lines
    
    @param img(Mat): matrix representation of image
    
    @return red_angle, steering_angle (int, int): angle of red shape and steering angle from lane lines
    """
    red = get_reds(img)
    #if no red detected default to 90 degrees
    try:
        red_angle = get_red_angle(red)
    except:
        red_angle = 90
    steering_angle = get_steering_angle(img)
    return red_angle, steering_angle
