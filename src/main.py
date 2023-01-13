from inputs import get_gamepad
import time

# local imports
import drive_module as dr
import steer_module as sr
import image_processing_module as ip

# import camera_module as cm
import quick_capture_module as qc
from matplotlib import pyplot as plt


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
                    # testing image taking
                    elif event.code == "BTN_WEST":
                        if event.state == 1:
                            image = stream.capture()
                            filtered = ip.image_changer(image)
                            # angle = ip.steering_output(ip.measure_angles(image))
                            plt.imshow(image)
                            plt.show(block=False)
                            plt.pause(5)
                            plt.imshow(filtered)
                            plt.show(block=False)
                            plt.pause(3)
                            plt.close()
                            # print(angle)
                    """
                    elif event.code == "BTN_SOUTH":
                        if event.state == 1:
                            image = camera.quick_capture()
                            plt.imshow(image)
                            plt.show()
                    """
                if event.ev_type == "Absolute":
                    if event.code == "ABS_RX":
                        x = float(event.state) / 32767.0
                        # print(x)
                        steer.steer(x)
                    elif event.code == "ABS_Y":
                        y = float(event.state) / 32767.0
                        drive.drive(y)
        except:
            # auto-navigation code here

            # steer.steer(ip.steering_output(ip.measure_angles(camera.capture())))
            """
            image = ip.image_changer(camera.capture())
            steering_angle = ip.steering_output(ip.measure_angles(image))
            print(steering_angle)
            steer.steer(steering_angle)
            time.sleep(1)
            """
            continue
    stream.stop()
    # camera.stop()
    steer.stop()
    steer.cleanup()


if __name__ == "__main__":
    main()
