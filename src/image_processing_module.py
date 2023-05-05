# imports
import cv2
import numpy as np
import math


def edge_detector(img):
    """
    @brief This function takes an image and returns it filtered for edges

    @param img(numpy array): A numpy array representation of image

    @return edges(numpy array): A numpy array representation of image with edges filtered
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = int(max(gray[0]) * 0.8)
    blur = cv2.GaussianBlur(gray, (21, 21), 0)
    ret, binary = cv2.threshold(blur, thresh, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(binary, 200, 400)
    return edges


def region_of_interest(edges):
    height, width = edges.shape
    mask = np.zeros_like(edges)

    # only focus bottom half of the screen
    polygon = np.array(
        [
            [
                (0, height * 1 / 2),
                (width, height * 1 / 2),
                (width, height),
                (0, height),
            ]
        ],
        np.int32,
    )

    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)
    return cropped_edges


def detect_line_segments(img):
    rho = 1  # distance precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
    min_threshold = 10  # minimal of votes
    line_segments = cv2.HoughLinesP(
        img, rho, angle, min_threshold, np.array([]), minLineLength=8, maxLineGap=4
    )
    return line_segments


def average_slope_intercept(frame, line_segments):
    lane_lines = []
    if line_segments is None:
        return []
        print("no lines")

    height, width, _ = frame.shape
    left_fit = []
    right_fit = []
    # horizontal_fit = []

    boundary = 1 / 3
    left_region_boundary = width * (
        1 - boundary
    )  # left lane line segment should be on left 2/3 of the screen
    right_region_boundary = (
        width * boundary
    )  # right lane line segment should be on right 2/3 of the screen

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


def display_lines(frame, lines, line_color=(255, 255, 255), line_width=2):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image


def compute_steering_angle(frame, lane_lines):

    if len(lane_lines) == 0:
        # continue straight if no lines
        return 90

    height, width = frame.shape[0], frame.shape[1]
    if len(lane_lines) == 1:
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
    else:
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        camera_mid_offset_percent = 0.02  # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
        mid = int(width / 2 * (1 + camera_mid_offset_percent))
        x_offset = (left_x2 + right_x2) / 2 - mid

    # find the steering angle, which is angle between navigation direction to end of center line
    y_offset = int(height / 2)

    angle_to_mid_radian = math.atan(
        x_offset / y_offset
    )  # angle (in radian) to center vertical line
    angle_to_mid_deg = int(
        angle_to_mid_radian * 180.0 / math.pi
    )  # angle (in degrees) to center vertical line
    steering_angle = (
        angle_to_mid_deg + 90
    )  # this is the steering angle 
    return steering_angle


def display_heading_line(
    frame,
    steering_angle,
    line_color=(0, 0, 255),
    line_width=5,
):
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


def lane_detection(img):
    edges = edge_detector(img)
    cropped_edges = region_of_interest(edges)
    line_segments = detect_line_segments(cropped_edges)
    lane_lines = average_slope_intercept(img, line_segments)
    line_image = display_lines(img, lane_lines)
    steering_angle = compute_steering_angle(line_image, lane_lines)
    final_image = display_heading_line(line_image, steering_angle)
    return final_image


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
    edges = edge_detector(img)
    cropped = region_of_interest(edges)
    line_segments = detect_line_segments(cropped)
    lane_lines = average_slope_intercept(img, line_segments)
    line_image = display_lines(img, lane_lines)
    steering_angle = compute_steering_angle(line_image, lane_lines)
    return steering_angle


def get_reds(img):
    invert = ~img
    hsv = cv2.cvtColor(invert, cv2.COLOR_BGR2HSV)
    lower_cyan = np.array([80, 150, 40])
    upper_cyan = np.array([100, 255, 255])
    mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
    #res = cv2.bitwise_and(img, img, mask= mask)
    return mask


def get_angle_image(img):
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
    red = get_reds(img)
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
    red = get_reds(img)
    red_angle = get_red_angle(red)
    steering_angle = get_steering_angle(img)
    return red_angle, steering_angle
