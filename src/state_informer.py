from threading import Thread
import math
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


class StateInformer:
    def __init__(self):
        # in variable names below, "distance" refers to values in pixels, and "deviation" refers to values in inches
        # "pos" refers to coordinates in image of the form (x-pixel, y-pixel)
        # NOTE: local function variables may not follow these rules. They should have comments
        self.thread: Thread = Thread(target = self.update_continuosly)
        self.speedometer: Speedometer = Speedometer().start()
        self.cam: Camera = Camera()
        self.car: Car = Car()

        self.lane_center_pos: tuple[int, int] = (0,0)
        self.lanes: list[tuple[float, float, float, float]] = []

        self.frame: cv2.Mat = self.cam.read() # ensure frame is non-None at start
        
        self.steering_angle: float = 0 # alpha
        self.car_lane_angle: float = 0 # theta1
        self.car_deviation: float = 0 # y1
        self.vel: float = 0 #v (assuming that car and trailer velocities are the same) (not how the paper does it)

        self.trailer_lane_angle: float = 0 # theta2
        self.hitch_angle: float = 0 # beta 
        self.trailer_pos: tuple[float, float] = (0, 0)
        self.trailer_deviation: float = 0 # y2

        self.CAMERA_LOCATION = self.frame.shape[1] / 2, self.frame.shape[0]
        self.HITCH_TO_TRAILER_AXLE_DIST = 8 # inches
        print(self.frame.shape)

        self.stopped: bool = False

    def update_vel(self):
        self.vel = self.speedometer.read()
    
    def get_vel(self):
        return self.vel

    def update_hitch_angle(self):
        # Relies on: update_trailer_pos()

        trailer_x, trailer_y = self.trailer_pos                                 
        cam_x, cam_y = self.CAMERA_LOCATION
        trailer_to_cam_line = math.dist(self.trailer_pos, self.CAMERA_LOCATION)
        trailer_to_frame_bottom_line = cam_y - trailer_y
        rad = math.acos(trailer_to_frame_bottom_line / trailer_to_cam_line)
        self.hitch_angle = math.degrees(rad)

        #          C    Point C: Camera Location (Car rear)
        #         /|    Point A: Trailer axle location (red marker)
        #        / |    Point B: Point defined by coordinates (x-coordiante of camera, y-coordinate of trailer) to ensure right triangle angle at all times.               
        #       /  |        
        #      /   |    Lengths of CA and CB are calculated. arccos(CB/CA) = angle C                 
        #     /____|        
        #    A      B   NOTE: arccos(1) = 0 so there is no problem when len(CA) = len(CB)
    
    def get_hitch_angle(self):
        return self.hitch_angle
    
    def update_trailer_pos(self):
        # Relies on: update_frame()
        img = self.frame
        red = iu.filter_red(img)
        self.trailer_pos = iu.weighted_center(red)
        
    def get_trailer_pos(self):
        return self.trailer_pos
    
    def update_trailer_lane_angle(self):
        # Relies on: update_trailer_pos(), update_lane_center_pos()
        trailer_x, trailer_y = self.trailer_pos
        lane_center_x, lane_center_y = self.lane_center_pos 
        cam_to_center_line = math.dist(self.CAMERA_LOCATION, (lane_center_x, trailer_y))
        cam_to_trailer_line = math.dist(self.CAMERA_LOCATION, self.trailer_pos)
        #print(cam_to_center_line, cam_to_trailer_line)
        #self.trailer_lane_angle =  math.degrees(math.acos(cam_to_center_line / cam_to_trailer_line))
        self.trailer_lane_angle = self.hitch_angle - self.car_lane_angle

        #          C    Point C: Camera Location (Car rear)
        #         /|    Point A: The trailer axle (red marker)
        #        / |    Point B: Defined by coordinate (x-coordinate of lane_center, y-coordinate of the trailer). Therefore the line CB is a line from camera to the lane center                    
        #       /  |     
        #      /   |                      
        #     /____|    A and B share the same y-coordinate so a right triangle is maintained 
        #    A      B   
        #               Finally, arccos(CB/CA) = angle C

    def get_trailer_lane_angle(self):
        return self.trailer_lane_angle

    
    def update_trailer_deviation(self):
        # Relies on: self.update_trailer_lane_angle()

        rad = math.radians(self.trailer_lane_angle)
        self.trailer_deviation = math.sin(rad) * self.HITCH_TO_TRAILER_AXLE_DIST

        #          C    Point C: Camera Location (Car rear)
        #         /|    Point A: The trailer axle (red marker)
        #        / |    Point B: Defined by coordinate (x-coordinate of lane_center, y-coordinate of the trailer).                    
        #       /  |     
        #      /   |                      
        #     /____|    A and B share the same y-coordinate so a right triangle is maintained 
        #    A      B   
        #               Length of line AB is the horizontal displacement of the trailer from the lane center.
        #               
        #               Known values are:
        #               - Angle C (self.trailer_lane_angle)
        #               - Length of CA (the physical distance from the hitch to the trailer axle)
        # 
        #               Desired value:
        #               - Length of AB
        #               
        #               sin(C) = BA/CA 
        #               CA * sin(C) = BA
        #

    def get_trailer_deviation(self):
        return self.trailer_deviation

   

    def update_car_lane_angle(self):
        # Relies on: update_lane_center_pos()
        
        cam_x, cam_y = self.CAMERA_LOCATION
        
        lane_center_x, lane_center_y = self.lane_center_pos
        

        central_line = math.dist(self.CAMERA_LOCATION, self.lane_center_pos)
        heading_line = cam_y - lane_center_y

        self.car_lane_angle = math.degrees(math.acos(heading_line / central_line))

        #          C    Point C: Camera Location (Car rear)
        #         /|    Point A: The center of the lane
        #        / |    Point B: Defined by coordinate (x-coordinate of lane_center, y-coordinate of the trailer).                  
        #       /  |    Therefore the line CB is the line from the camera  
        #      /   |                      
        #     /____|    A and B share the same y-coordinate so a right triangle is maintained 
        #    A      B   
        #               Finally, arccos(CB/CA) = angle C

    def get_car_lane_angle(self):
        return self.car_lane_angle
    
    def update_car_deviation(self):
        # Relies on: update_trailer_deviation(), update_car_lane_angle()

        # represent left and right both as positive numbers?
        true_distance_to_center = math.sqrt (self.HITCH_TO_TRAILER_AXLE_DIST**2 + self.trailer_deviation**2) # inches
        horizontal_distance_to_center = true_distance_to_center * math.sin(math.radians(self.car_lane_angle)) # inches
        self.car_deviation = horizontal_distance_to_center # inches


        #           C
        #          / \           Point C: Camera Location
        #         / | \          Point B: Point defined by (x-coordinate of lane center, y-coordinate of trailer)
        #        /  |  \         Point A: Trailer axle location (red marker)                     
        #       /   |   \        Point D: Point defining heading line of camera (CD) such that it intersects with AB
        #      /    |    \                  
        #     /_____|_____\      NOTE: Triangle CBD is right; triangle ABC is a triangle. 
        #    A      D      B 
        #               
        #                       Known values are:
        #                       - Length of CA (HITCH_TO_AXLE_DISTANCE)
        #                       - Length of AB (self.trailer_deviation)
        #                       - Angle DCB (self.car_lane_angle)
        #                         
        #                        
        #                       Desired value:
        #                       - length of DB
        #               
        #                       
        #
        #                       By pythagorean theorem, length of CB = sqrt(HITCH_TO_AXLE_DISTANCE^2 + self.trailer_deviation^2)
        #                       
        #                       CBD is a right triangle (I'm like 99% sure but I'm not gonna prove it)
        #
        #                       If CB is the distance between the car and lane center (the x-cooordinate of point B is the lane center x-coordinate),
        #                       then the x component of CB is the horizontal distance of the car from the center
        #
        #                       sin(DCB) = length DB / length CB
        #                       length CB * sin(DCB) = length DB
        #                       

    def get_car_deviation(self):
        return self.car_deviation


    def update_steering_angle(self):
        #Relies on: car.set_steering_angle()
        self.steering_angle = self.car.current_steering_angle
    
    def get_steering_angle(self):
        return self.steering_angle
    
    def update_lanes(self):
        # Relies on: update_frame()
        img = self.frame
        edges = ip.edge_detector(img)
        cropped_edges = ip.region_of_interest(edges)
        line_segments = ip.detect_line_segments(cropped_edges)
        lane_lines = ip.average_slope_intercept(img, line_segments)
        self.lanes = lane_lines
    
    def get_lanes(self):
        return self.lanes
    
    def update_lane_center_pos(self):
        #Relies on: update_lanes()
        if len(self.lanes) == 2:

            lane1 = self.lanes[0]
            lane1_x1, lane1_y1, lane1_x2, lane1_y2 = lane1
            lane1_midpoint = iu.midpoint((lane1_x1, lane1_y1), (lane1_x2, lane1_y2))

            lane2 = self.lanes[1]
            lane2_x1, lane2_y1, lane2_x2, lane2_y2 = lane2
            lane2_midpoint = iu.midpoint((lane2_x1, lane2_y1),(lane2_x2, lane2_y2))

            #self.lane_center_pos = ((lane1_midpoint[0]+lane2_midpoint[0])/2, 240)
            self.lane_center_pos = iu.midpoint(lane1_midpoint, lane2_midpoint)

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

    def get_lane_center_pos(self):
        return self.lane_center_pos

    def update_state(self):
        self.update_frame() # This one needs to be first; the others rely on it.

        self.update_vel()

        self.update_trailer_pos()
        
        self.update_lanes()
        self.update_lane_center_pos()


        self.update_steering_angle()
        self.update_car_lane_angle()
        self.update_hitch_angle()
        self.update_trailer_lane_angle()

        self.update_trailer_deviation()
        self.update_car_deviation()
        

    def update_frame(self):
        self.frame = self.cam.read()

    def update_continuosly(self):
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





    

        

