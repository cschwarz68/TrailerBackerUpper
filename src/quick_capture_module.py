"""
This is a Python script that uses the Raspberry Pi camera module (specifically the picamera2 library) to capture and process images in real-time.
It defines a StreamCamera class that initializes and controls the camera.
The `capture` method captures an image from the camera and returns a OpenCV matrix / numpy array representing the image, after rotating and converting it to RGB format.

The main script creates an instance of the StreamCamera class, captures an image in a loop, applies some image processing techniques from the image_processing_module, 
displays the resulting image using the OpenCV library, and exits when the 'q' key is pressed.
Finally, it calls the stop method to stop the camera preview and close the camera.

Note: If the images change to fast or an extreme angle is detected, numpy will emit a RuntimeWarning. This is okay.
"""

# Package Imports
from picamera2 import Picamera2 # Using version 0.3.9!
import numpy as np
import cv2

# Local Imports
from constants import OpenCV_Settings
import image_processing_module as ip
class StreamCamera:
    def __init__(self):
        self.camera = Picamera2()
        # Adjust camera parameters. Using defaults.

        # self.camera.preview_configuration.main.format = Camera_Settings.PREVIEW_CONFIG_FORMAT
        # self.camera.resolution = Camera_Settings.RESOLUTION
        # self.camera.framerate = Camera_Settings.FRAMERATE
        # self.camera.start_preview(alpha=Camera_Settings.ALPHA)

        self.camera.start()

    # Takes an image input and applies a 90 degree rotation twice and color change from BGR to RGB.
    def capture(self):
        array = self.camera.capture_array()
        array = np.rot90(array, 2)
        array = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
        return array

    def stop(self):
        self.camera.stop_preview()
        self.camera.close()

    """

    Everything beneath this comment is for testing.

    """

# Unit Test
if __name__ == "__main__":
    camera = StreamCamera()
    debug_output = []

    """
    IMPORTANT

    VSCode's video player thinks the video is corrupt. Use VLC Media Player.
    """
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    base_height, base_width, _ = camera.capture().shape
    video = cv2.VideoWriter("quick_capture_module_test_video.mp4", fourcc, OpenCV_Settings.RECORDING_FRAMERATE, (base_width, base_height), isColor=True)
    print(f"Recording with dimensions {base_width}x{base_height} with FPS {OpenCV_Settings.RECORDING_FRAMERATE}.")

    while True:
        image = camera.capture()

        # Normal lane detection.
        steering_angle_deg, lane_lines = ip.steering_info(image)
        image = ip.display_lanes_and_path(image, steering_angle_deg, lane_lines)
        cv2.imshow("Quick Capture Module Unit Test - Auto Forward Lanes and Path", image)
        lane_lines_len = len(lane_lines)

        # Print debugging while the camera is running decreases performance likely due to stdout buffering.
        # Print the entire thing on exit.
        debug_output.append("Angle: " + str(steering_angle_deg) + "\t" + (
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
