from picamera2 import Picamera2 # Using version 0.3.9!
import numpy as np
import cv2

# Local Imports
import image_processing_module as ip
from constants import Drive_Params, Camera_Settings

from quick_capture_module import StreamCamera

camera = StreamCamera()
debug_output = []

"""
IMPORTANT

VSCode's video player thinks the video is corrupt. Use VLC Media Player.
"""
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
base_height, base_width, _ = camera.capture().shape
video = cv2.VideoWriter("quick_capture_module_test_video.mp4", fourcc, Camera_Settings.FRAMERATE, (base_width, base_height), isColor=True)
print(f"Recording with dimensions {base_width}x{base_height} with FPS {Camera_Settings.FRAMERATE}.")

while True:
    image = camera.capture()

    # Normal lane detection.
    steering_angle_deg, lane_lines = ip.steering_info(image)
    image = ip.display_lanes_and_path(image, steering_angle_deg, lane_lines)
    cv2.imshow("Quick Capture Module Unit Test - Auto Forward Lanes and Path", image)
    lane_lines_len = len(lane_lines)

    # Print debugging while the camera is running decreases performance likely due to stdout buffering.
    # Print the entire thing on exit.
    debug_output.append("Angle: " + str(steering_angle_deg - Drive_Params.STEERING_RACK_CENTER) + "\t" + (
        "No Lanes" if lane_lines_len == 0 
        else "One Lane: " + str(lane_lines[0]) if lane_lines_len == 1 
        else "Left Lane: " + str(lane_lines[0]) + " | Right Lane: " + str(lane_lines[1])
    ))

    # Video
    image = cv2.resize(image, (base_width, base_height))
    video.write(image)

    # Exit upon pressing (q). Make sure the preview window is focused.
    # The 0xFF is a bitmask which makes it work with NumLock on.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.stop()
video.release()
cv2.destroyAllWindows()
for msg in debug_output:
    print(msg)