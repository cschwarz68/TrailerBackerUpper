import cv2
import image_processing as ip
from constants import Reverse_Calibrations
import os


# TODO: This can probably go into model.py at some point
# ALSO TODO: actually make the neural network work in some nontrivial way...

def create_frame(source_file):
    cap = cv2.VideoCapture(source_file)
    angle = 0
    try:
        i = 0
        while cap.isOpened():
            _, image = cap.read()
            angle = get_angle(image)
            os.chdir('/home/nads/Documents/Python/TrailerBackerUpper/src/frames2')
            cv2.imwrite("%s_%03d_%03d.png" % (source_file, i, angle), image)
            os.chdir('..')
            i += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

def get_angle(image):
    # Lanes
    edges = ip.edge_detector(image)
    cropped_edges = ip.region_of_interest(edges)
    line_segments = ip.detect_line_segments(cropped_edges)
    lane_lines = ip.average_slope_intercept(image, line_segments)
    num_lanes = len(lane_lines)
    steering_angle_lanes = ip.compute_steering_angle(image, lane_lines)

    # Trailer
    filtered = ip.filter_red(image)
    cropped = ip.region_of_interest(filtered, True)
    cx, cy = ip.weighted_center(cropped)
    trailer_points = (image.shape[1] / 2, image.shape[0], cx, cy)
    hitch_angle = ip.compute_hitch_angle(image, cx, cy)
    trailer_angle = hitch_angle - steering_angle_lanes # Angle of the trailer relative to the lane center.

    steering_angle = 0
    if num_lanes == 2:
        lane_center_x = (lane_lines[0][2] + lane_lines[1][2]) / 2
        trailer_deviation = cx - lane_center_x
        _, width, _ = image.shape

        if abs(trailer_deviation) > width * Reverse_Calibrations.POSITION_THRESHOLD:
            steering_angle = steering_angle_lanes * Reverse_Calibrations.TURN_RATIO * -1
            # If the trailer is not centered, steer to the center.

        if abs(hitch_angle) > Reverse_Calibrations.HITCH_ANGLE_THRESHOLD:
            steering_angle = hitch_angle * Reverse_Calibrations.TURN_RATIO
            # If the angle of the hitch is too great, reduce it.
    
        if abs(trailer_angle) > Reverse_Calibrations.ANGLE_OFF_CENTER_THRESHOLD:
            steering_angle = trailer_angle * Reverse_Calibrations.TURN_RATIO
            # If the angle of the trailer relative to lane center is too great, reduce it.
    else:
        # If two lanes are not visible.

        steering_angle = 0 # TODO: Make this actually be useful.

    return -steering_angle

if __name__ == "__main__":
    create_frame('straight_line_training.avi')

