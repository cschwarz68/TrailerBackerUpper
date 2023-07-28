import cv2
import numpy as np
import image_processing as ip
import image_utils as iu
from threading import Thread
from car import Car
from camera import Camera
from speedometer import Speedometer

# TODO: Come up with a nice name for this module and class
# Working name: StateInformer get it like state informer like a spy? It's so funny.

class StateInformer:
    def __init__(self):
        self.thread = Thread(target = self.poll_state_info)
        self.stopped=False
        self.steering_angle = 0
        self.vel = 0
        self.hitch_angle = 0
        self.lane_pos = 0
        self.trailer_x, self.trailer_y = 0, 0
        self.car = Car()
        self.cam = Camera()
        self.frame = self.cam.read() # ensure frame is non-None at start
        self.speedometer = Speedometer().start()
        self.lanes = []
        self.lane_center: tuple[int, int] = (0,0)
        self.trailer_deviation = 0


    def update_vel(self):
        self.vel = self.speedometer.read()
    
    def get_vel(self):
        return self.vel

    def update_hitch_angle(self):
        img: cv2.Mat = self.frame
        origin_x, origin_y = img.shape[1] / 2, img.shape[0]
        x_offset, y_offset = self.trailer_x - origin_x, origin_y - self.trailer_y
        angle = np.arctan(x_offset / y_offset)
        angle = np.degrees(angle)
    
    def get_hitch_angle(self):
        return self.hitch_angle
    
    def update_trailer_pos(self):
        img = self.frame
        red = iu.filter_red(img)
        trailer_x, trailer_y = iu.weighted_center(red)
        
    def get_trailer_pos(self):
        return self.trailer_x, self.trailer_y
    
    def update_trailer_deviation(self):
        x,y = self.lane_center
        self.trailer_deviation = self.trailer_x - x


    def update_steering_angle(self):
        self.steering_angle = self.car.current_steering_angle
    
    def get_steering_angle(self):
        return self.steering_angle
    
    def update_lanes(self, img: cv2.Mat):
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

            self.lane_center = iu.midpoint(lane1_midpoint, lane2_midpoint)

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
        self.stopped = True
        self.thread.join()
        print("StateInformer resources released.")

    

        

