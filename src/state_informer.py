import math
import time
from imutils import contours, perspective
from threading import Thread
from math import dist
import numpy as np
import imutils
import cv2
# LOCAL IMPORTS
from constants import ImageProcessingCalibrations as Calibrations
from speedometer import Speedometer
import image_processing as ip
import image_utils as iu
from camera import Camera
from car import Car

# TODO: Come up with a nice name for this module and class
# Working name: StateInformer get it like state informer like a spy? It's so funny.

# This module tracks all relevant vehicle state information needed for implemeneting model predictive control
# as described in http://liu.diva-portal.org/smash/get/diva2:1279885/FULLTEXT01.pdf (pdf available in ../literature)

PIXELS_TO_INCHES_RATIO = Calibrations.PIXELS_TO_INCHES_RATIO

class StateInformer:
    def __init__(self):
        # in variable names below, "distance" refers to values in pixels, and "deviation" refers to values in inches
        self.thread: Thread = Thread(target = self.poll_state_info)
        self.speedometer: Speedometer = Speedometer().start()
        self.cam: Camera = Camera()
        self.car: Car = Car()

        self.lane_center: tuple[int, int] = (0,0)
        self.lanes: list[tuple[float, float, float, float]] = []

        self.frame: cv2.Mat = self.cam.read() # ensure frame is non-None at start
        
        self.steering_angle: float = 0 # alpha
        self.car_lane_angle: float = 0 # theta0
        self.car_deviation: float = 0 # y1
        self.vel: float = 0

        self.trailer_angle: float = 0 # theta1
        self.hitch_angle: float = 0 # beta 
        self.trailer_distance_to_car = 0
        self.trailer_pos: tuple[float, float] = (0, 0)
        self.trailer_deviation: float = 0 # y2

        self.camera_location = self.frame.shape[1] / 2, self.frame.shape[0]
        print(self.frame.shape)

        self.stopped: bool = False

    def update_vel(self):
        self.vel = self.speedometer.read()
    
    def get_vel(self):
        return self.vel

    def update_hitch_angle(self):
        img: cv2.Mat = self.frame
        trailer_x, trailer_y = self.trailer_pos
        origin_x, origin_y = img.shape[1] / 2, img.shape[0]
        x_offset, y_offset = trailer_x - origin_x, origin_y - trailer_y
        angle = np.arctan(x_offset / y_offset)
        angle = np.degrees(angle)
    
    def get_hitch_angle(self):
        return self.hitch_angle
    
    def update_trailer_pos(self):
        img = self.frame
        red = iu.filter_red(img)
        self.trailer_pos = iu.weighted_center(red)
        
    def get_trailer_pos(self):
        return self.trailer_pos
    
    def update_trailer_deviation(self):
        self.trailer_deviation = dist(self.trailer_pos, self.lane_center) * PIXELS_TO_INCHES_RATIO

    def update_trailer_distance_to_car(self):
        self.trailer_distance_to_car = dist(self.trailer_pos, self.camera_location)

    def update_car_lane_angle(self):
        img = self.frame 
        
        frame_center_x, frame_center_y = img.shape[1], img.shape[0]
        
        lane_center_x, lane_center_y = self.lane_center
        

        central_line = math.dist(self.camera_location, self.lane_center)
        heading_line = math.dist(self.camera_location, (frame_center_x, lane_center_y))

        self.car_lane_angle = math.degrees(math.acos(central_line, heading_line))

    def get_car_lane_angle(self):
        return self.car_lane_angle
       


    def update_steering_angle(self):
        self.steering_angle = self.car.current_steering_angle
    
    def get_steering_angle(self):
        return self.steering_angle
    
    def update_lanes(self):
        img = self.frame
        edges = ip.edge_detector(img)
        cropped_edges = ip.region_of_interest(edges)
        line_segments = ip.detect_line_segments(cropped_edges)
        lane_lines = ip.average_slope_intercept(img, line_segments)
        self.lanes = lane_lines
    
    def get_lanes(self):
        return self.lanes
    
    def update_lane_center(self):
        if len(self.lanes) == 2:

            lane1 = self.lanes[0]
            lane1_x1, lane1_y1, lane1_x2, lane1_y2 = lane1
            lane1_midpoint = iu.midpoint((lane1_x1, lane1_x2), (lane1_y1, lane1_y2))

            lane2 = self.lanes[1]
            lane2_x1, lane2_y1, lane2_x2, lane2_y2 = lane2
            lane2_midpoint = iu.midpoint((lane2_x1, lane2_x2),(lane2_y1, lane2_y2))

            self.lane_center = iu.midpoint(lane1_midpoint, lane2_midpoint) # type: ignore

            # I'm not sure if this is really what I want for the lane center. Perhaps the midpoint of the forward most points of the lane
            # would be better because avoiding displacement is better than correcting it.
        elif len(self.lanes) == 1:
            pass

        # Here's what I'd like to do if there is one lane:
        # Whenever there are two lanes, we record the distance from the left lane to the center, and the distance from the right lane to the center.
        # When two lanes are no longer visible, we check whether the visible lane is on the left or on the right.
        # We use the corresponding previously saved distance to estimate a new lane center. In vertical (not actually considered due to infinite slope)
        #  or near-vertical lane conditions,
        # A line can simply be drawn from the midpoint of the lane to the left or right. However, in a curve, a line like this would not allign with the true center.
        # A better approximation would be a line perpendicular to the drawn lane line.
        # I'll get around to this eventually, for now I'll see how well (probably not very well) it works when only updating the lane center when two lanes are visible.
        #TODO (maybe): I think it would be beneficial if the center of the lanes was the refernce point (perhaps implemented as cartesian origin) for other positions.

    def get_lane_center(self):
        return self.lane_center

    def update_state(self):
        self.read_camera() # This one needs to be first; the others rely on it.
        self.update_vel()
        self.update_lanes()
        self.update_hitch_angle()
        self.update_steering_angle()
        self.update_trailer_pos()
        

    def read_camera(self):
        self.frame = self.cam.read()

    def poll_state_info(self):
        while not self.stopped:
            self.update_state()
    
    def start(self):
        self.thread.start()
        return self

    def stop(self):
        self.speedometer.stop()
        print("Releasing state informer resources... ", end="")
        self.stopped = True
        self.thread.join()
        print("DONE")


if __name__ == "__main__":
    this = StateInformer()
    cam = Camera().start()
    time.sleep(2)
    img = cam.read()
    red = iu.filter_red(img)
    edges = ip.edge_detector(red)
    cntrs = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cntrs = imutils.grab_contours(cntrs)
    (cntrs, _) = contours.sort_contours(cntrs, method = "top_to_bottom")
    red_tape = cntrs[0]
    box = cv2.minAreaRect(red_tape)
    box = cv2.boxPoints(box)
    box = np.array( box, dtype="int")

    box = perspective.order_points(box)
    cX = np.average(box[:,0])
    cY = np.average(box[:,1])

    tl, tr, bl, br = box
    top_mid = iu.midpoint(tl,tr)
    bottom_mid = iu.midpoint(bl,br)

    distance  = math.dist(top_mid, bottom_mid)

    ratio = distance / (7/8) # seven eighths inches lol

    print(ratio)
    print(distance)


  
    cv2.imwrite("contours.png", edges)
    this.stop()
    cam.stop()



    

        

