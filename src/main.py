"""
This is the main program.
There are three modes: manual, forward autonomous, and reverse autonomous.

Upon start, if the controller is found, the program defaults to manual mode.

Forward autonomous mode can be entered by pressing (X) and then (START).
Reverse autonomous mode can be entrered by pressing (Y) and then (START).
    Return to manual mode by pressing (B).

Exit manual mode / the program by pressing (B).
"""

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
steer = None
drive = None
stream = None
mode = Main_Mode.MANUAL
transition_mode = Main_Mode.AUTO_FORWARD
controller_present = True
# Loops until (b) is pressed.
done = False

"""
This commented code is a replacement for get_pressed should the latter be buggy.
"""
# # Less efficient than the previous method of iterating though the events a single time 
# # and using conditionals within the loop, but also more concise.
# def is_pressed(events, type : str, code : str, state : int) -> tuple[bool, Any]:
#     # There does not appear to be a better method for detecting button presses 
#     # other than iterating through the entire list.
#     for event in events:
#         if (event.ev_type == type and 
#             event.code == code and 
#             state is None or event.state == state):
#             return (True, event)
#     return (False, None)

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
    global done, steer, drive, mode, transition_mode
    """
    This commented code uses the is_pressed function.
    Use in case get_pressed is buggy.
    """
    # if is_pressed(events, "Key", "BTN_EAST", 1)[0]:
        # done = True
    # elif is_pressed(events, "Key", "BTN_SOUTH", 1)[0]:
        # pass # Bypassing functionality for now.
        # video_capture()
    # event_x = is_pressed(events, "Absolute", "ABS_RX", None)[1] # RX refers to the right joystick.
    # event_y = is_pressed(events, "Absolute", "ABS_Y", None)[1]
    # if event_x is not None:
    #     x = float(event_x.state) / Drive_Params.TURN_MAX
    #     steer.steer(x)
    # if event_y is not None:
    #     y = float(event_y.state) / Drive_Params.TURN_MAX
    #     drive.drive(-y)
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
    elif pressed["Key"]["BTN_SOUTH"] == 1:
        pass # Bypassing functionality for now.
        # video_capture()
    elif pressed["Key"]["BTN_NORTH"] == 1:
        transition_mode = Main_Mode.AUTO_FORWARD
        print("Transitioned to auto FORWARD. Press START to init.")
    elif pressed["Key"]["BTN_WEST"] == 1:
        transition_mode = Main_Mode.AUTO_REVERSE
        print("Transitioned to auto REVERESE. Press START to init.")
    elif pressed["Key"]["BTN_START"] == 1:
        print("Entered Mode:", transition_mode)
        mode = transition_mode
    x = pressed["Absolute"]["ABS_RX"]
    y = pressed["Absolute"]["ABS_Y"]
    if x is not None:
        steer.steer(x / Drive_Params.JOYSTICK_MAX)
    if y is not None:
        drive.drive(-y / Drive_Params.JOYSTICK_MAX)

def auto_forward():
    global stream, steer, drive
    if check_auto_exit():
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
    if check_auto_exit():
        return
    pass

def check_auto_exit():
    global controller_present, mode
    if controller_present:
        events = get_gamepad()
        pressed = get_pressed(events, [
            ("Key", "BTN_EAST")
        ])
        if pressed["Key"]["BTN_EAST"] == 1:
            mode = Main_Mode.MANUAL
            drive.drive(0)
            steer.steer_by_angle(Drive_Params.TURN_STRAIGHT)
            print("Returning To:", mode)
            return True
    return False

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
            auto_forward()
        elif mode == Main_Mode.AUTO_REVERSE:
            auto_reverse()

    steer.stop()
    steer.cleanup()

    # Currently bypassed functionality.
    # stream.stop()
    # camera.stop()
    # out.release()

def video_capture(): # SEEMS TO BE CURRENTLY BROKEN
    global stream, steer
    # Processing and capture test.
    image = stream.capture()
    edges = ip.edge_detector(image)
    cropped_edges = ip.region_of_interest(edges)
    line_segments = ip.detect_line_segments(cropped_edges)
    lane_lines = ip.average_slope_intercept(image, line_segments)
    # num_lanes = len(lane_lines)
    line_image = ip.display_lines(image, lane_lines)
    # Recording.
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(
        "test_recording.mp4", fourcc, 20.0, (320, 240)
    )
    while True:
        frame = cv2.cvtColor(
            np.array(line_image), cv2.COLOR_GRAY2BGR
        )
        out.write(frame)
        steering_angle = ip.compute_steering_angle(
            line_image, lane_lines
        )
        steer.steer_by_angle(steering_angle)

if __name__ == "__main__":
    main()
