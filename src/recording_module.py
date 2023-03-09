# local imports
#import quick_capture_module as qc
import image_processing_module as ip
import steer_module as sr

# other imports
import cv2
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
import time


def save_video():
    camera = Picamera2()
    camera.resolution = (640, 480)
    video_config = camera.create_video_configuration()
    camera.configure(video_config)

    encoder = H264Encoder(bitrate=1_000_000)
    output = 'video_test2.h264'
    time.sleep(15)
    camera.start_recording(encoder, output)
    time.sleep(15)
    camera.stop_recording()

    # time.sleep(15)

    # camera.start_recording("test_captures/video_test2.h264", format="h264")
    # time.sleep(10)

    # camera.stop_recording()
    camera.close()


def modify_video():
    steer = sr.Steer()
    video_directory = "test_captures"
    video_file = video_directory + "/video_test2"
    path_to_folder = "test_capture/video_testing2/"
    cap = cv2.VideoCapture(video_file + ".h264")

    try:
        i = 0
        while cap.isOpened():
            _, frame = cap.read()
            edges = ip.edge_detector(frame)
            cropped_edges = ip.region_of_interest(edges)
            line_segments = ip.detect_line_segments(cropped_edges)
            lane_lines = ip.average_slope_intercept(frame, line_segments)
            num_lanes = len(lane_lines)
            steering_angle = ip.get_steering_angle(frame)
            stable_angle = steer.stabilize_steering_angle(steering_angle, num_lanes)
            cv2.imwrite("%s_%03d_%03d.png" % (video_file, i, steering_angle), frame)
            #cv2.imwrite(f"test_captures/video_testing/video01_{i}_{steering_angle}.png", frame)
            i += 1
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    modify_video()
    #save_video()
