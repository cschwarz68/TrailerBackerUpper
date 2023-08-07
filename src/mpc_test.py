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

from car import Car
from state_informer import StateInformer

def handler(signum: signal.Signals, stack_frame):
    global done
    print("\nKeyboard interrupt detected.")
    done = True
    # print(signum, signal.Signals(signum).name, stack_frame) 
    cleanup()
signal.signal(signal.SIGINT, handler) # type: ignore


def cleanup():
    global state_informer, car, cam, streamer

    print("Cleaning up...")


    state_informer.stop()
    car.stop()
    car.cleanup()
    cam.stop()
    streamer.stop()

    # Video
    # video.release()

    print("Cleaned up.")
    exit(0)

if __name__ == "__main__":
    predicter = Predicter()

    car = Car()
    g = Gamepad()
    cam = Camera().start()
    state_informer: StateInformer = StateInformer().start()
    streamer: UDPStreamer = UDPStreamer().start()
    time.sleep(2)
    car.set_steering_angle(0)
    start = time.time()

    car.set_drive_power(-.7)
    i = 0
    while(True): #(time.time()<start+10):
        streamer.stream_image(state_informer.frame)
        #car.set_drive_power(0)
        angle, cost = predicter.predict(state_informer)
        plt.plot(cost)
        plt.savefig("car_cost" + str(i)+ ".png")

        car.set_steering_angle(angle)
        car.set_drive_power(-.7)
        i+=1
    
    cleanup()
    



