import pygame

# local imports
import controller_module as js
import drive_module as dr
import steer_module as sr


def main():
    pygame.init()

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    steer = sr.Steer()
    drive = dr.Drive()

    # Loop until the user clicks the close button.
    done = False
    while not done:
        # Process events
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                print("Quit")
                done = True  # Flag that we are done so we exit this loop

            # Possible joystick actions:
            # JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
            if event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.")
                if js.joystick.get_button(1):  # 'X'
                    done = True
            if event.type == pygame.JOYBUTTONUP:
                print("Joystick button released.")

        values = js.update()
        steer.steer(values["axes"][3])
        drive.drive(values["axes"][1])

        # Limit to 10 frames per second
        clock.tick(10)

    steer.stop()
    steer.cleanup()


if __name__ == "__main__":
    main()
