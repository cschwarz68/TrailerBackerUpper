from inputs import get_gamepad
import time

# local imports
import drive_module as dr
import steer_module as sr
import image_processing_module as ip
# import camera_module as cm

import quick_capture_module as qc
#from matplotlib import pyplot as plt
import cv2
import logging
import numpy as np


def main():
    print("starting main program")

    steer = sr.Steer()
    drive = dr.Drive()
    stream = qc.StreamCamera()
    # camera = cm.Camera()

    # test steering upon startup
    """
    steer.steer(-0.5)
    time.sleep(0.5)
    steer.steer(0.5)
    time.sleep(0.5)
    steer.steer(0)
    """
    # Loop until the user clicks the close button.
    done = False
    while not done:
        try:
            events = get_gamepad()
            # Process events
            for event in events:
                if event.ev_type == "Key":
                    if event.code == "BTN_EAST":
                        if event.state == 1:
                            done = True
                    # processing and capture test
                    elif event.code == "BTN_SOUTH":
                        if event.state == 1:
                            pass
                            # image = camera.quick_capture()
                            image = stream.capture()
                            # final_image = ip.lane_detection(image)
                            edges = ip.edge_detector(image)
                            cropped_edges = ip.region_of_interest(edges)
                            line_segments = ip.detect_line_segments(cropped_edges)
                            lane_lines = ip.average_slope_intercept(image, line_segments)
                            num_lanes = len(lane_lines)
                            line_image = ip.display_lines(image, lane_lines)

                            # # recording
                            # fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                            # out = cv2.VideoWriter(
                            #     "test_recording.mp4", fourcc, 20.0, (320, 240)
                            # )
                            # while True:
                            #     frame = cv2.cvtColor(
                            #         np.array(line_image), cv2.COLOR_GRAY2BGR
                            #     )
                            #     out.write(frame)

                            #steering_angle = ip.compute_steering_angle(
                            #     line_image, lane_lines
                            # )
                            # steer.steer_by_angle(steering_angle)
                if event.ev_type == "Absolute":
                    if event.code == "ABS_RX":
                        x = float(event.state) / 32767.0
                        # print(x)
                        steer.steer(x)
                    elif event.code == "ABS_Y":
                        y = float(event.state) / 32767.0
                        drive.drive(-y)
        except:
            # auto-navigation code here

            # steer.steer(ip.steering_output(ip.measure_angles(camera.capture())))
            image = stream.capture()
            # cv2.imshow("heading", image)
            # if cv2.waitKey(1) & 0xFF == ord("q"):
            #     break
            """
            filtered = ip.image_changer(image)
            angles = ip.measure_angles(filtered)
            steer_angle = ip.steering_output(angles)
            print(angles, ip.steering_output(angles))
            steer.steer(steer_angle)
            """

            # testing auto-navigation with houghlines
            edges = ip.edge_detector(image)
            # cv2.imshow("heading", edges)
            # if cv2.waitKey(1) & 0xFF == ord("q"):
            #     break
            cropped_edges = ip.region_of_interest(edges)
            line_segments = ip.detect_line_segments(cropped_edges)
            lane_lines = ip.average_slope_intercept(image, line_segments)
            num_lanes = len(lane_lines)
            line_image = ip.display_lines(image, lane_lines)
            # cv2.imshow("heading", line_image)
            # if cv2.waitKey(1) & 0xFF == ord("q"):
            #     break
            steering_angle = ip.compute_steering_angle(line_image, lane_lines)

            if abs(steering_angle - 90) > 7.5:
                drive.drive(0.7)
            else:
                drive.drive(0.6)


            # steering_image = ip.display_heading_line(line_image, steering_angle)
            # cv2.imshow("heading", steering_image)
            # if cv2.waitKey(1) & 0xFF == ord("q"):
            #     break

            stable_angle = steer.stabilize_steering_angle(steering_angle, num_lanes)

            # logging.basicConfig(
            #     filename="steering.log",
            #     filemode="w",
            #     format="%(message)s",
            #     level=logging.INFO,
            # )
            # logging.info(
            #     f"steering angle: {str(steering_angle)} stabilized angle: {str(stable_angle)}"
            # )

            steer.steer_by_angle(stable_angle)

            continue
    # stream.stop()
    # camera.stop()
    steer.stop()
    steer.cleanup()
    # out.release()


if __name__ == "__main__":
    main()
