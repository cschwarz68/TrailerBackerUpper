"""
This is the main program.
There are three modes: manual, forward autonomous, and reverse autonomous.

Upon start, if the controller is found, the program defaults to manual mode.

Forward autonomous mode can be entered by pressing (X) and then (START).
Reverse autonomous mode can be entrered by pressing (Y) and then (START).
    Return to manual mode by pressing (B).

Press (A) to enable recording for autonomous mode.

Exit manual mode / the program by pressing (B).
"""

from threading import Thread
import signal

# Package Imports
import cv2

# Local Imports
from constants import Main_Mode, Drive_Params, OpenCV_Settings
from gamepad import Gamepad, Inputs as inputs
from motor import cleanup as GPIO_cleanup
import image_processing_module as ip
import quick_capture_module as qc
from car import Car

# Mutable
transition_mode = Main_Mode.AUTO_FORWARD
check_auto_exit_thread = None
controller_present = True
mode = Main_Mode.MANUAL
auto_exit = False
recording = False

stream = qc.StreamCamera()
g      = Gamepad()
car    = Car()

# Video. Use VLC Media Player because VSCode's player thinks it's corrupt.
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
base_height, base_width, _ = stream.capture().shape
video = cv2.VideoWriter("main_video.mp4", 
                        fourcc, OpenCV_Settings.RECORDING_FRAMERATE, 
                        (base_width, base_height), 
                        isColor=True)

# Loops until (b) is pressed.
done = False

# Trigger cleanup upon keyboard interrupt.
def handler(signum: signal.Signals, stack_frame):
    print("Keyboard interrupt detected. Cleaning up.")
    print(signum, signal.Signals(signum).name, stack_frame)
    car.set_drive_power(0)
    car.set_steering_angle(0)
    cleanup()
signal.signal(signal.SIGINT, handler)

def manual():
    global done, mode, transition_mode, check_auto_exit_thread, recording

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
        check_auto_exit_thread = Thread(target=check_auto_exit)
        check_auto_exit_thread.start()
        print("Entered Mode:", transition_mode)
    elif g.was_pressed(inputs.A):
        if not recording:
            recording = True
            print("Enabled Recording for Autonomous")
        else:
            recording = False
            print("Disabled Recording for Autonomous")

    steer_value = g.get_stick_value(inputs.LX)
    drive_value = g.get_trigger_value()
    if steer_value is not None:
        car.gamepad_steer(steer_value)
    if drive_value is not None:
        car.gamepad_drive(drive_value)

def auto_forward():
    global stream, auto_exit, recording
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

    # Go faster on sharper turns.
    if abs(steering_angle) > Drive_Params.SHARP_TURN_DEGREES:
        car.set_drive_power(0.7)
    else:
        car.set_drive_power(0.6)
    stable_angle = car.stabilize_steering_angle(steering_angle, num_lanes)
    car.set_steering_angle(stable_angle)

    if recording:
        visual_image = ip.display_lanes_and_path(image, steering_angle, lane_lines)
        video.write(visual_image)

def auto_reverse():
    # Not yet implemented.
    if auto_exit:
        exit_auto()
        return

    if recording:
        visual_image = ip.display_lanes_and_path(image, steering_angle, lane_lines)
        video.write(visual_image)

def check_auto_exit():
    global mode, auto_exit
    while mode != Main_Mode.MANUAL:
        g.update_input()
        if g.was_pressed(inputs.B):
            auto_exit = True
            return

def exit_auto():
    global mode, check_auto_exit_thread, auto_exit
    mode = Main_Mode.MANUAL
    car.set_drive_power(0)
    car.set_steering_angle(0)
    check_auto_exit_thread.join()
    auto_exit = False
    print("Returning To:", mode)

def main():
    print("STARTING MAIN")

    global stream, done, mode, controller_present

    try:
        g.update_input()
    except:
        print("Plug in gamepad to start.")
        exit(1)

    # Main loop.
    while not done:
        # Detect if controller is plugged in.
        if mode == Main_Mode.MANUAL:
            try:
                g.update_input()
            except:
                print("CONTROLLER DISCONNECTED")
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

def cleanup():
    stream.stop()
    car.stop()
    GPIO_cleanup()

    # Video
    video.release()

if __name__ == "__main__":
    #server_child = Thread(target=server_main)
    #server_child.start()
    main()
    #server_child.kill()
    #server_child.join()
