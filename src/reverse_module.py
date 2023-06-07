from inputs import get_gamepad
import drive_module as dr
import steer_module as sr
import quick_capture_module as qc
import image_processing_module as ip
import cv2
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder


def reverse_straight():
    steer = sr.Steer()
    drive = dr.Drive()
    camera = qc.StreamCamera()

    while True:
        image = camera.capture()
        # edges = ip.edge_detector(image)
        red = ip.get_reds(image)
        try:
            red_angle = ip.get_red_angle(red)
        except:
            red_angle = 90

        # lane_angle = ip.get_steering_angle(image)
        # diff_in_angles = red_angle - lane_angle

        # cv2.imshow("heading", edges)
        # if cv2.waitKey(1) & 0xFF == ord("q"):
        #     break
        # cropped_edges = ip.region_of_interest(edges)
        # line_segments = ip.detect_line_segments(cropped_edges)
        # lane_lines = ip.average_slope_intercept(image, line_segments)
        # num_lanes = len(lane_lines)
        # line_image = ip.display_lines(image, lane_lines)
        # cv2.imshow("heading", line_image)
        # if cv2.waitKey(1) & 0xFF == ord("q"):
        #     break
        # steering_angle = ip.compute_steering_angle(line_image, lane_lines)
        #steer.trailer_steering_test(steering_angle)
        steer.steer_by_angle(180-red_angle - 6.5) # -6 to account for tendency to go to the left
        #steer.steer_by_angle( 90 - diff_in_angles)
        drive.drive(-0.62)


def reverse_and_lanes():
    steer = sr.Steer()
    drive = dr.Drive()
    camera = qc.StreamCamera()

    while True:
        image = camera.capture()
        red = ip.get_reds(image)
        try:
            red_angle = ip.get_red_angle(red)
        except:
            red_angle = 90

        lane_angle = ip.get_steering_angle(image)
        diff_in_angles = red_angle - lane_angle
        #print(f"redang = {red_angle}, laneang = {lane_angle}")
        steer.steer_by_angle( 90 - diff_in_angles, 1.8)
        drive.drive(-0.62)


def self_and_controller_reverse():
    steer = sr.Steer()
    drive = dr.Drive()
    camera = qc.StreamCamera()
    while True:
        print(1)
        events = get_gamepad()
        print(2)
        event = events[0]
        image = camera.capture()
        red = ip.get_reds(image)
        try:
            red_angle = ip.get_red_angle(red)
        except:
            red_angle = 90
        print(event)
        if event.ev_type == "Absolute":
            if event.code == "ABS_RX":
                x = float(event.state) / 32767.0
                # print(x)
                steer.steer(x)
            elif event.code == "ABS_Y":
                y = float(event.state) / 32767.0
                drive.drive(-y)
            elif event.code != "ABS_RX":
                steer.steer_by_angle(180-red_angle - 6.5)
        # for event in events:
        #     print(type(events))
        #     print(len(events))
        #     # while :
        #     #     image = camera.capture()
        #     #     red = ip.get_reds(image)
        #     try:
        #         red_angle = ip.get_red_angle(red)
        #     except:
        #         red_angle = 90
        #     if event.ev_type == "Absolute":
        #         if event.code == "ABS_RX":
        #             x = float(event.state) / 32767.0
        #             print(x)
        #             steer.steer(x)
        #         elif event.code == "ABS_Y":
        #             y = float(event.state) / 32767.0
        #             drive.drive(-y)
        #         elif event.code != "ABS_RX":
        #             steer.steer_by_angle(180-red_angle - 6.5)


def drive_tester():
    drive = dr.Drive()
    steer = sr.Steer()
    while True:
        events = get_gamepad()
        for event in events:
            if event.ev_type == "Key":
                # if b pressed, fast loop
                if event.code == "BTN_EAST":
                    if event.state == 1:
                        start_time = time.time()
                        while time.time() < start_time + 3:
                            drive.drive(1)
                        drive.drive(0)
                        print('done')

                # if a pressed, slow loop
                elif event.code == "BTN_SOUTH":
                    if event.state == 1:
                        start_time = time.time()
                        while time.time() < start_time + 3:
                            time.sleep(1)
                            drive.drive(1)
                        drive.drive(0)
                        print('done')

                # if x pressed, drive and steer test    
                elif event.code == "BTN_NORTH":
                    start_time = time.time()
                    while time.time() < start_time + 3:
                        drive.drive(0.7)
                        steer.steer_by_angle(120)
                    steer.steer_by_angle(90)
                    drive.drive(0)

            if event.ev_type == "Absolute":
                    if event.code == "ABS_RX":
                        x = float(event.state) / 32767.0
                        # print(x)
                        steer.steer(x)
                    elif event.code == "ABS_Y":
                        y = float(event.state) / 32767.0
                        print(y)
                        drive.drive(-y)
    

        
def save_video():
    camera = Picamera2()
    camera.resolution = (640, 480)
    video_config = camera.create_video_configuration()
    camera.configure(video_config)

    encoder = H264Encoder(bitrate=1_000_000)
    output = 'reverse_capture.h264'
    camera.start_recording(encoder, output)
    time.sleep(7.5)
    camera.stop_recording()
def modify_video():
    steer = sr.Steer()
    video_directory = "test_captures/reverse_captures"
    video_file = video_directory + "/reverse_capture"
    path_to_folder = "test_captures/reverse_captures/"
    cap = cv2.VideoCapture(video_file + ".h264")
    try:
        i = 0
        while cap.isOpened():
            _, frame = cap.read()
            cv2.imwrite("%s_%03d.png" % (video_file, i), frame)
            i += 1
    finally:
        cap.release()
        cv2.destroyAllWindows()
if __name__ == "__main__":
    # reverse_straight()
    # self_and_controller_reverse()
    # reverse_and_lanes()
    drive_tester()