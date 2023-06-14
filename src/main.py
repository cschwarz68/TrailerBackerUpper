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

# Local Imports
from gamepad import Gamepad, Inputs as inputs
from car import Car
import image_processing_module as ip
import quick_capture_module as qc
from constants import Main_Mode, Drive_Params
from motor import cleanup as GPIO_cleanup

# Mutable
stream = None #
mode = Main_Mode.MANUAL
transition_mode = Main_Mode.AUTO_FORWARD
controller_present = True
check_auto_exit_thread = None
auto_exit = False

car = Car()
g = Gamepad()

# Loops until (b) is pressed.
done = False


def manual():
    global done, mode, transition_mode, check_auto_exit_thread
   
    if g.was_pressed(inputs.B):
        done = True
    elif g.was_pressed(inputs.X):
        transition_mode = Main_Mode.AUTO_FORWARD
        print("Transitioned to auto FORWARD. Press START to init.")
    elif g.was_pressed(inputs.Y):
        transition_mode = Main_Mode.AUTO_REVERSE
        print("Transitioned to auto REVERESE. Press START to init.")
    elif g.was_pressed(inputs.START):
        mode = transition_mode
        check_auto_exit_thread = Thread (target=check_auto_exit)
        check_auto_exit_thread.start()
        print("Entered Mode:", transition_mode)
    steer_value = g.get_stick_value(inputs.LX)
    drive_value = g.get_trigger_value()
    if steer_value is not None:
        car.gamepad_steer(steer_value)
    if drive_value is not None:
        car.gamepad_drive(drive_value)

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
    steering_angle = ip.compute_steering_angle(image, lane_lines)

    # Go faster on sharper turns? ¯\_(ツ)_/¯
    if abs(steering_angle - Drive_Params.TURN_STRAIGHT) > Drive_Params.SHARP_TURN_DEGREES:
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
        if g.was_pressed(inputs.B):
            auto_exit = True
            return

def exit_auto():
    global mode, check_auto_exit_thread, auto_exit
    mode = Main_Mode.MANUAL
    car.gamepad_drive(0)
    car.gamepad_steer(Drive_Params.STEERING_RACK_CENTER)
    check_auto_exit_thread.join()
    auto_exit = False
    print("Returning To:", mode)

def main():
    print("STARTING MAIN")
    

    global tream, done, mode, controller_present
    stream = qc.StreamCamera()

    try:
        g.update_input()
    except:
        print("Plug in gamepad to start.")
        exit(1)

    #main loop
    while not done:
        # Detect if controller is plugged in.
        if mode == Main_Mode.MANUAL:
            try:
                g.update_input()
            except:
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

    
    stream.stop()
    car.stop()
    GPIO_cleanup()

if __name__ == "__main__":
    main()
