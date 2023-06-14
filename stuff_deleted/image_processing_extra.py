
# Everything beneath this comment has not been refactored.

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
