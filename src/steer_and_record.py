#imports
from inputs import get_gamepad
import cv2
import time

#local imports
import drive_module as dr
import steer_module as sr
import image_processing_module as ip
import quick_capture_module as qc

path_to_file = "test_captures/steer_captures/test1"

def main():
    steer = sr.Steer()
    drive = dr.Drive()
    stream = qc.StreamCamera()
    time.sleep(10)
    i = 0
    while True:
        drive.drive(0.805)
        image = stream.capture()
        steering_angle = 90
        events = get_gamepad()
        for event in events:
                if event.ev_type == "Key":
                    if event.code == "BTN_EAST":
                        if event.state == 1:
                            break
                if event.ev_type == "Absolute":
                    if event.code == "ABS_RX":
                        x = float(event.state) / 32767.0
                        steering_angle = (x*45)+90
                        steer.steer(x)
        cv2.imwrite("%s_%03d_%03d.png" % (path_to_file, i, steering_angle), image)
        i += 1
if __name__ == "__main__":
    main()
