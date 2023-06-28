"""
This is the main program.
There are three modes: manual, forward autonomous, and reverse autonomous.

Also contains streaming and recording capabilities.

Exit manual mode / the program by pressing (B).
"""

from threading import Thread
import signal, socket

# Package Imports
import cv2

# Local Imports
from constants import Main_Mode, Drive_Params, OpenCV_Settings, Reverse_Calibrations
from gamepad import Gamepad, Inputs as inputs
from motor import cleanup as GPIO_cleanup
from streaming import FrameSegment
import image_processing as ip
import camera as cam
from car import Car

class Main:
    # Mutable
 
    def __init__(self):

        self.transition_mode = Main_Mode.AUTO_FORWARD
        self.check_auto_exit_thread = None
        self.controller_present = True
        self.mode = Main_Mode.MANUAL
        self.frame_segment = None
        self.auto_exit = False
        self.recording = False
        self.streaming = False


        self.stream = cam.Camera()
        self.g      = Gamepad()
        self.car    = Car()

        # Video. Use VLC Media Player because VSCode's player thinks it's corrupt.
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        base_height, base_width, _ = self.stream.capture().shape
        self.video = cv2.VideoWriter("main_video.mp4", 
                                fourcc, OpenCV_Settings.RECORDING_FRAMERATE, 
                                (base_width, base_height), 
                                isColor=True)

        # Loops until (b) is pressed.
        self.done = False

    # Trigger cleanup upon keyboard interrupt.
    def handler(self, signum: signal.Signals, stack_frame):
        print("Keyboard interrupt detected. Cleaning up.")
        print(signum, signal.Signals(signum).name, stack_frame) 
        self.cleanup()
    signal.signal(signal.SIGINT, handler)

    def manual(self):
        g = self.g
        car = self.car

        if g.was_pressed(inputs.B):
            self.done = True
        elif g.was_pressed(inputs.X):
            transition_mode = Main_Mode.AUTO_FORWARD
            print("Transitioned to auto FORWARD. Press START to init.")
        elif g.was_pressed(inputs.Y):
            transition_mode = Main_Mode.AUTO_REVERSE
            print("Transitioned to auto REVERESE. Press START to init.")
        elif g.was_pressed(inputs.START):
            self.mode = transition_mode
            check_auto_exit_thread = Thread(target=self.check_auto_exit)
            check_auto_exit_thread.start()
            print("Entered Mode:", transition_mode)
        elif g.was_pressed(inputs.A):
            if not recording:
                recording = True
                print("Enabled Recording for Autonomous")
            else:
                recording = False
                print("Disabled Recording for Autonomous")
        elif g.was_pressed(inputs.SELECT):
            if not streaming:
                streaming = True
                print("Enabled Streaming for Autonomous")
            else:
                streaming = False
                print("Disabled Streaming for Autonomous")

        steer_value = g.get_stick_value(inputs.LX)
        drive_value = g.get_trigger_value()
        if steer_value is not None:
            car.gamepad_steer(steer_value)
        if drive_value is not None:
            car.gamepad_drive(drive_value)
        
        # if streaming:
        #     image = stream.capture()
        #     stream_to_client(image)


    def auto_forward(self):
        car = self.car
        if self.auto_exit:
            self.exit_auto()
            return
        image = self.stream.capture()
        edges = ip.edge_detector(image)
        cropped_edges = ip.region_of_interest(edges)
        line_segments = ip.detect_line_segments(cropped_edges)
        lane_lines = ip.average_slope_intercept(image, line_segments)
        num_lanes = len(lane_lines)
        steering_angle = ip.compute_steering_angle(image, lane_lines)

        # Go faster on sharper turns.
        if abs(steering_angle) > Drive_Params.SHARP_TURN_DEGREES:
            car.set_drive_power(0.9)
        else:
            car.set_drive_power(1.0)
        stable_angle = car.stabilize_steering_angle(steering_angle, num_lanes)
        car.set_steering_angle(stable_angle)

        # Video
        if self.recording or self.streaming:
            visual_image = ip.display_lanes_and_path(image, steering_angle, lane_lines)

            if self.streaming:   
                self.stream_to_client(visual_image)
            if self.recording:
                self.video.write(visual_image)

    def auto_reverse(self):
        if self.auto_exit:
            self.exit_auto()
            return
        image = self.stream.capture()

        # Lanes
        edges = ip.edge_detector(image)
        cropped_edges_lower = ip.region_of_interest(edges)
        cropped_edges_upper = ip.region_of_interest(edges, True)
        line_segments_lower = ip.detect_line_segments(cropped_edges_lower)
        line_segments_upper = ip.detect_line_segments(cropped_edges_upper)
        lane_lines_lower = ip.average_slope_intercept(image, line_segments_lower)
        lane_lines_upper = ip.average_slope_intercept(image, line_segments_upper)
        num_lanes = len(lane_lines_lower)
        steering_angle_lanes = ip.compute_steering_angle(image, lane_lines_lower)

        # Trailer
        filtered = ip.filter_red(image)
        cropped = ip.region_of_interest(filtered, True)
        cx, cy = ip.center_red(cropped)
        trailer_points = ip.Line(image.shape[1] / 2, image.shape[0], cx, cy)
        hitch_angle = ip.compute_hitch_angle(image, cx, cy)
        trailer_angle = hitch_angle - steering_angle_lanes # Angle of the trailer relative to the lane center.

        steering_angle = 0
        _, width, _ = image.shape
        if num_lanes == 2:
            lane_center_x = (lane_lines_lower[0].x2 + lane_lines_lower[1].x2) / 2
            trailer_deviation = cx - lane_center_x
            

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
            lane_x = lane_lines_lower[0].x2
            trailer_distance_from_lane = abs(lane_x-cx)
        
            

            if abs(trailer_distance_from_lane) > width * Reverse_Calibrations.POSITION_THRESHOLD:
                steering_angle = steering_angle_lanes * Reverse_Calibrations.TURN_RATIO * -1
                # If the trailer is not centered, steer to the center.

            if abs(hitch_angle) > Reverse_Calibrations.HITCH_ANGLE_THRESHOLD:
                steering_angle = hitch_angle * Reverse_Calibrations.TURN_RATIO
                # If the angle of the hitch is too great, reduce it.
        
            if abs(trailer_angle) > Reverse_Calibrations.ANGLE_OFF_CENTER_THRESHOLD:
                steering_angle = trailer_angle * Reverse_Calibrations.TURN_RATIO
                # If the angle of the trailer relative to lane center is too great, reduce it.


        # Redundant, but may need to adjust speed in the future.
        car = self.car
        if abs(steering_angle) > Drive_Params.SHARP_TURN_DEGREES_REVERSE:
            car.set_drive_power(-.8)
        else:
            car.set_drive_power(-.8)
        stable_angle = car.stabilize_steering_angle(steering_angle, num_lanes)
        car.set_steering_angle(-stable_angle)

        # Video
        if self.recording or self.streaming:
            visual_image = ip.display_lanes_and_path(image, steering_angle, lane_lines_lower)
            visual_image = ip.display_lanes_and_path(image, steering_angle, lane_lines_upper)
            visual_image = ip.display_trailer_info(visual_image, trailer_angle, trailer_points)

            if self.streaming:
                self.stream_to_client(cropped_edges_lower)
            if self.recording:
                self.video.write(visual_image)

    def get_slope(self, line: ip.Line):
        return (line.y2 - line.y1 ) / (line.x2 - line.x1)

    def check_auto_exit(self):
        g = self.g
        while self.mode != Main_Mode.MANUAL:
            g.update_input()
            if g.was_pressed(inputs.B):
                self.auto_exit = True
                return

    def exit_auto(self):
        self.mode = Main_Mode.MANUAL
        car = self.car
        car.set_drive_power(0)
        car.set_steering_angle(0)
        self.check_auto_exit_thread.join()
        self.auto_exit = False
        print("Returning To:", self.mode)

    def main(self):
        mode = self.mode
        print("STARTING MAIN")
        g = self.g


        # Streaming
        server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        port = 25565
        """
        IMPORTANT

        Insert the IP address of the device to stream to.
        """
        addr = "192.168.2.185"
        self.frame_segment = FrameSegment(server_socket, port, addr)

        try:
            g.update_input()
        except:
            go = input("Are you sure you want to start without gamepad? Will automatically enter autonomous mode: ").casefold()
            if go == "y" or go == "yes":
                go_mode = input("Autonomous Mode. 1 for forward, 2 for reverse: ")
                if go_mode == "1":
                    mode = Main_Mode.AUTO_FORWARD
                elif go_mode == "2":
                    mode = Main_Mode.AUTO_REVERSE
                else:
                    print("Invalid mode.")
                    exit(0)
            else:
                exit(0)

        # Main loop.
        while not self.done:
            # Detect if controller is plugged in.
            if mode == Main_Mode.MANUAL:
                try:
                    g.update_input()
                except:
                    print("CONTROLLER DISCONNECTED")
                    mode = self.transition_mode
                    self.controller_present = False
                    print("Entered Mode:", self.transition_mode)
            
            if mode == Main_Mode.MANUAL:
                self.manual()
            elif mode == Main_Mode.AUTO_FORWARD:
                # Need to move the camera to the front so it can see ahead. Take note of new and former positions!
                self.auto_forward()
            elif mode == Main_Mode.AUTO_REVERSE:
                self.auto_reverse()

        server_socket.close()
        self.cleanup()

    def stream_to_client(self,stream_image: cv2.Mat):
        if self.streaming:
            self.frame_segment.udp_frame(stream_image)

    def cleanup(self):
        self.stream.stop()
        self.car.stop()
        GPIO_cleanup()

        # Video
        self.video.release()

        print("Cleaned up.")

if __name__ == "__main__":
    main = Main()
    main.main()
