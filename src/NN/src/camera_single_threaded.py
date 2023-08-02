"""
This is a Python script that uses the Raspberry Pi camera module (specifically the picamera2 library) to capture and process images in real-time.
It defines a StreamCamera class that initializes and controls the camera.
The `capture` method captures an image from the camera and returns a OpenCV matrix / numpy array representing the image, after rotating and converting it to RGB format.

The main script creates an instance of the StreamCamera class, captures an image in a loop, applies some image processing techniques from the image_processing_module, 
displays the resulting image using the OpenCV library, and exits when the 'q' key is pressed.
Finally, it calls the stop method to stop the camera preview and close the camera.

Note: If the images change too fast or an extreme angle is detected, numpy will emit a RuntimeWarning. This is okay.
"""

# Package Imports
from picamera2 import Picamera2 # Using version 0.3.9!
import numpy as np
import cv2, sys

# Local Imports
from constants import OpenCVSettings
import image_processing as ip
import image_utils as iu

class Camera:
    
    def __init__(self, cam_num=0, framerate= 15):
        self.camera = Picamera2(cam_num)
      
        
        
        # Adjust camera parameters. Using defaults.

        # self.camera.preview_configuration.main.format = Camera_Settings.PREVIEW_CONFIG_FORMAT
        # self.camera.resolution = Camera_Settings.RESOLUTION
        self.camera.framerate = framerate
        # self.camera.start_preview(alpha=Camera_Settings.ALPHA)

        self.camera.start()

    # Takes an image input and applies a 90 degree rotation twice and color change from BGR to RGB.
    # The rotation is necessary because the camera is mounted upside down.
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
    camera = Camera()
    debug_output = []

    """
    IMPORTANT

    VSCode's video player thinks the video is corrupt. Use VLC Media Player.
    """
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    base_height, base_width, _ = camera.capture().shape
    video = cv2.VideoWriter("quick_capture_module_test_video.mp4", fourcc, OpenCVSettings.RECORDING_FRAMERATE, (base_width, base_height), isColor=True)
    print(f"Recording with dimensions {base_width}x{base_height} with FPS {OpenCVSettings.RECORDING_FRAMERATE}.")

    go = input("Mode. 1 --> forward, 2 --> reverse: ")

    while True:
        image = camera.capture()
        reduced = iu.combine_images([(image, 0.25)]) # Reduce opacity of base image.

        if go == "1":
            # Normal lane detection.
            steering_angle_deg, lane_lines = ip.steering_info(image)
            image = ip.display_lanes_and_path(reduced, steering_angle_deg, lane_lines)
            cv2.imshow("Quick Capture Module Unit Test - Auto Forward Lanes and Path", image)
            lane_lines_len = len(lane_lines)

            # Print debugging while the camera is running decreases performance likely due to stdout buffering.
            # Print the entire thing on exit.
            debug_output.append(f"Angle: {steering_angle_deg}\t" + (
                "No Lanes" if lane_lines_len == 0 
                else "One Lane: " + str(lane_lines[0]) if lane_lines_len == 1 
                else "Left Lane: " + str(lane_lines[0]) + " | Right Lane: " + str(lane_lines[1])
            ))
        elif go == "2":
            # Trailer detection.
            steering_angle_deg, lane_lines = ip.steering_info(image)
            trailer_angle, trailer_points = ip.steering_info_reverse(image)
            image = ip.display_lanes_and_path(reduced, steering_angle_deg * -1, lane_lines)
            image = ip.display_trailer_info(image, trailer_angle, trailer_points)
            cv2.imshow("Quick Capture Module Unit Test - Auto Forward Lanes and Path with Trailer", image)

            # See comment above.
            debug_output.append(f"Trailer Angle: {trailer_angle}")
        else:
            break

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
