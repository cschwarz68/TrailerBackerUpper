from inputs import get_gamepad
import time

# local imports
import drive_module as dr
import steer_module as sr


def main():
    print("starting main program")

    steer = sr.Steer()
    drive = dr.Drive()

    # test steering upon startup
    steer.steer(-0.5)
    time.sleep(0.5)
    steer.steer(0.5)
    time.sleep(0.5)
    steer.steer(0)

    # Loop until the user clicks the close button.
    done = False
    while not done:
        events = get_gamepad()
        # Process events
        for event in events:
            if event.ev_type == "Key":
                if event.code == "BTN_EAST":
                    if event.state == 1:
                        done = True
            if event.ev_type == "Absolute":
                if event.code == "ABS_RX":
                    x = float(event.state) / 32767.0
                    steer.steer(x)
                elif event.code == "ABS_Y":
                    y = float(event.state) / 32767.0
                    drive.drive(y)

    steer.stop()
    steer.cleanup()


if __name__ == "__main__":
    main()
