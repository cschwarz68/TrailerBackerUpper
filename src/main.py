"""
This is the main program.
There are three modes: manual, forward autonomous, and reverse autonomous.

Also contains streaming and recording capabilities.

Exit manual mode / the program by pressing (B).
"""

from threading import Thread
import signal, socket, traceback, time

# Package Imports
import cv2

# Local Imports
from constants import Main_Mode, Drive_Params, OpenCV_Settings, Reverse_Calibrations, Streaming
from gamepad import Gamepad, Inputs, UnpluggedError
from streaming import FrameSegment
import image_processing as ip
from camera import Camera
from car import Car

# Mutable
transition_mode = Main_Mode.AUTO_FORWARD
check_auto_exit_thread = None
manual_streaming_thread = None
controller_present = True
mode = Main_Mode.MANUAL
frame_segment = None
auto_exit = False
recording = False

cam    = Camera()
g      = Gamepad()
car    = Car()

# Video. Use VLC Media Player because VSCode's player thinks it's corrupt.
fourcc = cv2.VideoWriter_fourcc(*"XVID")
base_height, base_width, _ = cam.capture().shape
video = cv2.VideoWriter("main_video.avi", 
                        fourcc, OpenCV_Settings.RECORDING_FRAMERATE, 
                        (base_width, base_height), 
                        isColor=True)

# Loops until (b) is pressed.
done = False

# Trigger cleanup upon keyboard interrupt.
def handler(signum: signal.Signals, stack_frame):
    print("Keyboard interrupt detected. Cleaning up.")
    print(signum, signal.Signals(signum).name, stack_frame) 
    cleanup()
signal.signal(signal.SIGINT, handler)

def manual():
    global done, mode, transition_mode, check_auto_exit_thread, recording, manual_streaming_thread


    #Streaming must be handled in its own thread in manual driving mode. see comments on stream_in_manual()
    if (manual_streaming_thread is None) or (not manual_streaming_thread.is_alive()): 
        manual_streaming_thread = Thread(target=stream_in_manual)
        manual_streaming_thread.start()




    if g.was_pressed(Inputs.B):
        done = True
    elif g.was_pressed(Inputs.X):
        transition_mode = Main_Mode.AUTO_FORWARD
        print("Transitioned to auto FORWARD. Press START to init.")
    elif g.was_pressed(Inputs.Y):
        transition_mode = Main_Mode.AUTO_REVERSE
        print("Transitioned to auto REVERESE. Press START to init.")
    elif g.was_pressed(Inputs.START):
        
        mode = transition_mode

        #Terminate thread for streaming in manual, since we are about to leave manual.
        if (manual_streaming_thread is not None) and (manual_streaming_thread.is_alive()):
            manual_streaming_thread.join()
        
        #Start thread to listen for instruction to return to manual mode
        check_auto_exit_thread = Thread(target=check_auto_exit)
        check_auto_exit_thread.start()
        print("Entered Mode:", transition_mode)
    elif g.was_pressed(Inputs.A):
        if not recording:
            recording = True
            print("Started Recording")
        else:
            recording = False
            print("Stopped Recording")
  


    

    steer_value = g.get_stick_value(Inputs.LX)
    drive_value = g.get_trigger_value()
    if steer_value is not None:
        car.gamepad_steer(steer_value)
    if drive_value is not None:
        car.gamepad_drive(drive_value)


def auto_forward():
    global cam, auto_exit, recording
    if auto_exit:
        exit_auto()
        return
    image = cam.capture()
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
    
    visual_image = ip.display_lanes_and_path(image, steering_angle, lane_lines)

    stream_to_client(visual_image)
    if recording:
        video.write(visual_image)

def maintain_hitch_angle(hitch_angle):
     if hitch_angle is not None and abs(hitch_angle) > Reverse_Calibrations.HITCH_ANGLE_THRESHOLD:
            return hitch_angle * Reverse_Calibrations.TURN_RATIO

def auto_reverse():
    global cam, auto_exit, recording
    if auto_exit:
        exit_auto()
        return
    image = cam.capture()
    raw_image = image

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

        if(abs(hitch_angle) > 30):
            car.jackknifed = True

       



        if abs(trailer_deviation) > width * Reverse_Calibrations.POSITION_THRESHOLD:
            steering_angle = steering_angle_lanes * Reverse_Calibrations.TURN_RATIO * -1
            # If the trailer is not centered, steer to the center.

        if abs(hitch_angle) > Reverse_Calibrations.HITCH_ANGLE_THRESHOLD:
            steering_angle = hitch_angle * Reverse_Calibrations.TURN_RATIO
            # If the angle of the hitch is too great, reduce it.
      
        if abs(trailer_angle) > Reverse_Calibrations.ANGLE_OFF_CENTER_THRESHOLD:
            steering_angle = trailer_angle * Reverse_Calibrations.TURN_RATIO
            # If the angle of the trailer relative to lane center is too great, reduce it.
        

        if(car.jackknifed): #if jackknifed, start driving forward to fix, will implement forward camera once we get USB adapter.
            steering_angle = steering_angle_lanes 
            drive_power = .7
            if abs(hitch_angle < 1):
                car.jackknifed = False #once angle is reduced, car will start reverse driving again
         
        else:
            car.set_steering_angle(-steering_angle_lanes)
            drive_power = -.7
        

    else: #code reuse because i still am not 100% sure how to handle 1 lane detected. Thinking 
      if(abs(hitch_angle) > 30):
            car.jackknifed = True
            
      if(car.jackknifed):
            if abs(hitch_angle < 5):
                car.jackknifed = False
            steering_angle = steering_angle_lanes 
            drive_power = .7
      else:
            car.set_steering_angle(-steering_angle_lanes)
            drive_power = -.7
        
        

    # Redundant, but may need to adjust speed in the future.
    # if abs(steering_angle) > Drive_Params.SHARP_TURN_DEGREES_REVERSE:
    #     car.set_drive_power(-.7)
    # else:
    car.set_drive_power(drive_power)
    stable_angle = car.stabilize_steering_angle(steering_angle, num_lanes)
    car.set_steering_angle(-stable_angle)

    # Video
    visual_image = ip.display_lanes_and_path(image, steering_angle, lane_lines)
    visual_image = ip.display_trailer_info(visual_image, hitch_angle, trailer_points)

    stream_to_client(visual_image)
    if recording:
        video.write(raw_image)

def check_auto_exit():
    global mode, auto_exit, recording
    """
    The initial function of this function was to listen for presses of B and return to manual mode if B was pressed.
    It now also allows enabling and disabling of recording while in autonomous driving modes. Should be renamed accordingly at some point
    """

    while mode != Main_Mode.MANUAL:
        g.update_input()
        if g.was_pressed(Inputs.B):
            auto_exit = True
            return
        if g.was_pressed(Inputs.A):
            if not recording:
                recording = True
                print("Started Recording")
            else:
                recording = False 
                print("Stopped Recording")

def exit_auto():
    global mode, check_auto_exit_thread, auto_exit
    mode = Main_Mode.MANUAL
    car.set_drive_power(0)
    car.set_steering_angle(0)
    check_auto_exit_thread.join()
    auto_exit = False
    print("Returning To:", mode)

def stream_in_manual():
    global recording
    """
    This function is the targert of manual_streaming_thread.

    cam.capture() hangs until a frame is supplied by the system. As a result, gamepad inputs can only be read when as frames are captured
    if g.update_input() and cam.capture() are called sequentially. Here, captures are offloaded to another thread whenever the car is in manual
    control mode.

    This function also records if recording is enabled. May need to rename it to something more general.
    """
    while True:
        image = cam.capture()
        
        stream_to_client(image)
        if recording:
            video.write(image)
        if g.was_pressed(Inputs.B) or mode != Main_Mode.MANUAL:
            break
        
        
def main():
    print("STARTING MAIN")

    global done, mode, controller_present, frame_segment

    # Streaming
    if Streaming.DO_STREAM:
        server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        port = Streaming.DESTINATION_PORT
    
        addr = Streaming.DESTINATION_ADDRESS
        frame_segment = FrameSegment(server_socket, port, addr)

    

    try:
        g.update_input()
    except UnpluggedError:
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
            print("Re-run with gamepad plugged in to start")
            exit(0)

    # Main loop.
    while not done:
        # Detect if controller is plugged in.
        if mode == Main_Mode.MANUAL:
            try:
                g.update_input()
            except Exception as e:
                print("update_input() threw an exception: ", e)
                traceback.print_exc()
                mode = transition_mode
                controller_present = False
                print("Entered Mode:", transition_mode)
        
        if mode == Main_Mode.MANUAL:
            manual()
        elif mode == Main_Mode.AUTO_FORWARD:
            # Need to move the camera to the front so it can see ahead. Take note of new and former positions!
            auto_forward()
        elif mode == Main_Mode.AUTO_REVERSE:
            auto_reverse()

    
    cleanup()
    if Streaming.DO_STREAM:
        server_socket.close() #Socket must be closed after calling cleanup() as a thread which may be using the socket is joined in cleanup.
    
    

def stream_to_client(stream_image: cv2.Mat):
    global frame_segment
    
    if Streaming.DO_STREAM:
        frame_segment.udp_frame(stream_image)

def cleanup():
    global cam, car, video, manual_streaming_thread
    print("Cleaning up...")
    if (manual_streaming_thread is not None) and (manual_streaming_thread.is_alive()):
        manual_streaming_thread.join()
    cam.stop()
    car.stop()
    car.cleanup()

    # Video
    
    video.release()

    print("Cleaned up.")

if __name__ == "__main__":
    main()
