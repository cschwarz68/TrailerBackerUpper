import drive_module as dr
import steer_module as sr
import quick_capture_module as qc
import image_processing_module as ip
import cv2
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder


def reverse():
    steer = sr.Steer()
    drive = dr.Drive()
    camera = qc.StreamCamera()

    while True:
        image = camera.capture()
        # edges = ip.edge_detector(image)
        red = ip.get_reds(image)
        try:
            steering_angle = ip.get_red_angle(red)
        except:
            steering_angle = 90
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
        steer.steer_by_angle(180-steering_angle)
        drive.drive(-0.7)
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
reverse()