"""
This is the main program.
There are three modes: manual, forward autonomous, and reverse autonomous.

Upon start, if the controller is found, the program defaults to manual mode.

Forward autonomous mode can be entered by pressing (X) and then (START).
Reverse autonomous mode can be entrered by pressing (Y) and then (START).
    Return to manual mode by pressing (B).

Exit manual mode / the program by pressing (B).
"""

from threading import Thread

# Package Imports
from inputs import get_gamepad
import numpy as np
import cv2

# Local Imports
import drive_module as dr
import steer_module as sr
import image_processing_module as ip
import quick_capture_module as qc
from constants import Main_Mode, Drive_Params

# Mutable
steer = None  #
drive = None  # Initialized in main.
stream = None #
mode = Main_Mode.MANUAL
transition_mode = Main_Mode.AUTO_FORWARD
controller_present = True
check_auto_exit_thread = None
auto_exit = False
# Loops until (b) is pressed.
done = False

def get_pressed(events, require : list[tuple[str, str]]) -> dict[str, dict[str, int]]:
    ret = dict()
    for key in require:
        if key[0] not in ret:
            ret[key[0]] = dict()
        ret[key[0]][key[1]] = None
    for event in events:
        # print(event.ev_type, event.code, event.state) # For debugging.
        if event.ev_type in ret and event.code in ret[event.ev_type]:
            ret[event.ev_type][event.code] = event.state
    return ret

def manual(events):
    global done, steer, drive, mode, transition_mode, check_auto_exit_thread
    """
    IMPORTANT

    On the controller:

            Y                  West
          X + B    -->    North + East
            A                 South
    """
    pressed = get_pressed(events, [
        ("Key", "BTN_EAST"), 
        ("Key", "BTN_SOUTH"), 
        ("Key", "BTN_WEST"), 
        ("Key", "BTN_NORTH"), 
        ("Key", "BTN_START"), 
        ("Absolute", "ABS_RX"), 
        ("Absolute", "ABS_Y")
    ])
    if pressed["Key"]["BTN_EAST"] == 1:
        done = True
    elif pressed["Key"]["BTN_NORTH"] == 1:
        transition_mode = Main_Mode.AUTO_FORWARD
        print("Transitioned to auto FORWARD. Press START to init.")
    elif pressed["Key"]["BTN_WEST"] == 1:
        transition_mode = Main_Mode.AUTO_REVERSE
        print("Transitioned to auto REVERESE. Press START to init.")
    elif pressed["Key"]["BTN_START"] == 1:
        mode = transition_mode
        check_auto_exit_thread = Thread (target=check_auto_exit)
        check_auto_exit_thread.start()
        print("Entered Mode:", transition_mode)
    x = pressed["Absolute"]["ABS_RX"]
    y = pressed["Absolute"]["ABS_Y"]
    if x is not None:
        steer.steer(x / Drive_Params.JOYSTICK_MAX)
    if y is not None:
        drive.drive(-y / Drive_Params.JOYSTICK_MAX)

def auto_forward():
    global stream, steer, drive, auto_exit
    if auto_exit:
        exit_auto()
        return
    image = stream.capture()
    edges = ip.edge_detector(image)
    cropped_edges = ip.region_of_interest(edges)
    line_segments = ip.detect_line_segments(cropped_edges)
    lane_lines = ip.average_slope_intercept(image, line_segments)
    num_lanes = len(lane_lines)
    line_image = ip.display_lines(image, lane_lines)
    steering_angle = ip.compute_steering_angle(line_image, lane_lines)
    if abs(steering_angle - Drive_Params.TURN_STRAIGHT) > 7.5:
        drive.drive(0.7)
    else:
        drive.drive(0.6)
    stable_angle = steer.stabilize_steering_angle(steering_angle, num_lanes)
    steer.steer_by_angle(stable_angle)

def auto_reverse():
    # Not yet implemented.
    if auto_exit:
        exit_auto()
        return
    pass

def check_auto_exit():
    global mode, auto_exit
    while mode != Main_Mode.MANUAL:
        events = get_gamepad()
        pressed = get_pressed(events, [
            ("Key", "BTN_EAST")
        ])
        if pressed["Key"]["BTN_EAST"] == 1:
            auto_exit = True
            return

def exit_auto():
    global mode, drive, steer, check_auto_exit_thread, auto_exit
    mode = Main_Mode.MANUAL
    drive.drive(0)
    steer.steer_by_angle(Drive_Params.TURN_STRAIGHT)
    check_auto_exit_thread.join()
    auto_exit = False
    print("Returning To:", mode)

def main():
    print("STARTING MAIN")

    global steer, drive, stream, done, mode, controller_present
    steer = sr.Steer()
    drive = dr.Drive()
    stream = qc.StreamCamera()

    try:
        get_gamepad()
    except:
        print("Plug in gamepad to start.")
        exit(1)

    #main loop
    while not done:
        # Detect if controller is plugged in.
        if mode == Main_Mode.MANUAL:
            try:
                events = get_gamepad()
            except:
                mode = transition_mode
                controller_present = False
                print("Entered Mode:", transition_mode)
        
        if mode == Main_Mode.MANUAL:
            manual(events)
        elif mode == Main_Mode.AUTO_FORWARD:
            # Need to move the camera to the front so it can see ahead. Take note of new and former positions!
            auto_forward()
        elif mode == Main_Mode.AUTO_REVERSE:
            auto_reverse()

    steer.stop()
    stream.stop()
    steer.cleanup()

if __name__ == "__main__":
    main()
