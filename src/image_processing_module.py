"""
Processes images with OpenCV for autonomous navigation.

IMPORTANT

All images are represented by OpenCV matrices, which are aliases of numpy arrays.
"""

import warnings
import math

# Package Imports
import numpy as np
import cv2

# Local Imports
from constants import Lane_Bounds_Ratio, Image_Processing_Calibrations

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
                (0, height / 2), 
                (width, height / 2), 
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

    # Because lane_lines will only ever have two values, we could return this as a tuple, but that would require unnecessary refactoring.
    return lane_lines

# Use lane lines to predict the steering angle in degrees.
# Arbitrary, maybe subject to change: 0 --> left, 90 --> straight, 180 --> right
def compute_steering_angle(frame: cv2.Mat, lane_lines: list[tuple[int, int, int, int]]) -> int:
    if len(lane_lines) == 0:
        # Continue straight if no lines are present...
        return 0

    height, width, _ = frame.shape
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
    return angle_to_mid_deg

"""

Everything beneath this comment is for testing.
Run `quick_capture_module.py` for unit tests.

"""

# Returns a black image with dimensions identical to that of the given image.
def zero_image(frame: cv2.Mat) -> cv2.Mat:
    return np.zeros_like(frame)

# Combines images together, where weight of each image can be adjusted.
# Images later in the list take z-axis priority.
def combine_images(pairs: list[tuple[cv2.Mat, float]]) -> cv2.Mat:
    # Throw exception if no images are provided.
    base = zero_image(pairs[0][0])
    for image, weight in pairs:
        # The last parameter is gamma, and is for adjusting the overall brightness.
        base = cv2.addWeighted(base, 1, image, weight, 0)
    return base

# Adds lines to image. Color is in RGB format.
def display_lines(img: cv2.Mat, lines: list[tuple[int, int, int, int]], line_color=(255, 255, 255), line_width=2) -> cv2.Mat:
    line_image = img.copy()
    if lines is None:
        return line_image
    for line in lines:
        x1, y1, x2, y2 = line
        cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    return line_image

# Returns the steering angle and lanes.
# Should be identical to the steps in main, but separate for testing.
def steering_info(img: cv2.Mat) -> tuple[int, list[tuple[int, int, int, int]]]:
    edges = edge_detector(img)
    cropped_edges = region_of_interest(edges)
    line_segments = detect_line_segments(cropped_edges)
    lane_lines = average_slope_intercept(img, line_segments)
    steering_angle_deg = compute_steering_angle(img, lane_lines)
    return (steering_angle_deg, lane_lines)

# Makes a black image containing lane lines and the calculated path. 
def display_lanes_and_path(img: cv2.Mat, steering_angle_deg: int, lane_lines: list[tuple[int, int, int, int]]) -> cv2.Mat:
    height, width, _ = img.shape
    steering_angle_radians = math.radians(steering_angle_deg + 90)

    # Calculations for the center path.
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radians))
    y2 = int(height / 2)

    final_image = combine_images([(img, 0.25)]) # Reduce opacity of base image.
    final_image = display_lines(final_image, lane_lines)
    final_image = display_lines(final_image, [(x1, y1, x2, y2)], (0, 255, 0))

    final_image = cv2.putText(final_image, "Steering Angle from Straight: " + str(steering_angle_deg), 
                              (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    return final_image
