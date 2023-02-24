# local imports
#import quick_capture_module as qc
import image_processing_module as ip

# other imports
import cv2
#import picamera
import time


# def save_video():
#     camera = picamera.PiCamera()
#     camera.resolution = (640, 480)
#     time.sleep(15)

#     camera.start_recording("test_captures/video_test.h264", format="h264")
#     time.sleep(10)

#     camera.stop_recording()
#     camera.close()


def modify_video():
    video_directory = "test_captures"
    video_file = video_directory + "/video_test"
    path_to_folder = "test_capture/video_testing/"
    cap = cv2.VideoCapture(video_file + ".h264")

    try:
        i = 0
        while cap.isOpened():
            _, frame = cap.read()
            steering_angle = ip.get_steering_angle(frame)
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
    # save_video()
