from threading import Thread
import signal, traceback

# Package Imports
import cv2


# Local Imports
from constants import MainMode, DriveParams, OpenCVSettings, ReverseCalibrations
from gamepad import Gamepad, Inputs, UnpluggedError
from streaming import UDPStreamer
import image_processing as ip
import image_utils as iu
from camera import Camera
from mpc import Predicter
import time
import matplotlib.pyplot as plt
from math import pi

from truck import Truck
from state_informer import StateInformer

def handler(signum: signal.Signals, stack_frame):
    global done
    print("\nKeyboard interrupt detected.")
    done = True
    # print(signum, signal.Signals(signum).name, stack_frame) 
    cleanup()
signal.signal(signal.SIGINT, handler) # type: ignore


def cleanup():
    global state_informer, truck, cam, streamer

    print("Cleaning up...")


    state_informer.stop()
    truck.stop()
    truck.cleanup()
    cam.stop()
    streamer.stop()

    # Video
    # video.release()

    print("Cleaned up.")
    exit(0)

if __name__ == "__main__":

    truck = Truck()
    g = Gamepad()
    cam = Camera().start()
    state_informer: StateInformer = StateInformer().start()
    predicter = Predicter(state_informer)
    streamer: UDPStreamer = UDPStreamer().start()
    time.sleep(2)
    truck.set_steering_angle(0)
    start = time.time()

    truck.set_drive_power(-.7)
    i = 0
    while(True): #(time.time()<start+10):
        state_vector = [0, state_informer.trailer_deviation, state_informer.trailer_lane_angle * pi / 180, state_informer.hitch_angle * pi / 180]
        streamer.stream_image(state_informer.frame)
        #car.set_drive_power(0)
        t, y, f, angle, next = predicter.predict_fast(truck.current_steering_angle, 1.4, 0, state_vector, 0.5)
        #plt.plot(cost)
        #plt.savefig("car_cost" + str(i)+ ".png")

        #print(angle)
        truck.set_steering_angle(angle)
        truck.set_drive_power(-.75)
        i+=1
    
    cleanup()
    



