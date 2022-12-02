import pygame
import RPi.GPIO as GPIO

# Define some colors
darkgrey = (40, 40, 40)
lightgrey = (150, 150, 150)

# Initialize the joysticks
pygame.joystick.init()

# Get count of joysticks
joystick_count = pygame.joystick.get_count()
print(f"{str(joystick_count)} joysticks detected")

# Get information on joystick 0
joystick = pygame.joystick.Joystick(0)
joystick.init()
name = joystick.get_name()
num_axes = joystick.get_numaxes()
num_buttons = joystick.get_numbuttons()
num_hats = joystick.get_numhats()
info = {
    "name": name,
    "num_axes": num_axes,
    "num_buttons": num_buttons,
    "num_hats": num_hats,
}
print(
    f"Joystick {name} has {str(num_axes)} axes, {str(num_buttons)} buttons, {str(num_hats)} hats"
)


def update():
    axes = []
    buttons = []
    hats = []

    for i in range(num_axes):
        axis = joystick.get_axis(i)
        axes.append(axis)

    for i in range(num_buttons):
        button = joystick.get_button(i)
        buttons.append(button)

    for i in range(num_hats):
        hat = joystick.get_hat(i)
        hats.append(hat)

    values = {"axes": axes, "buttons": buttons, "hats": hats}
    return values


class TextPrint:
    """
    This is a simple class that will help us print to the screen
    """

    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def print(self, screen, textString):
        textBitmap = self.font.render(textString, True, lightgrey)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


def show(screen, textPrint, values):
    # DRAWING STEP
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(darkgrey)
    textPrint.reset()
    textPrint.print(screen, f"Number of joysticks: {joystick_count}")
    textPrint.indent()
    textPrint.print(screen, f"Joystick name: {name}")
    textPrint.print(screen, f"Number of axes: {num_axes}")
    textPrint.indent()
    for i, axis in enumerate(values["axes"]):
        textPrint.print(screen, f"Axis {i} value: f{axis:>6.2f}")
    textPrint.unindent()
    textPrint.print(screen, f"Number of buttons: {num_buttons}")
    textPrint.indent()
    for i, button in enumerate(values["buttons"]):
        textPrint.print(screen, f"Button {i} value: {button:>6.0f}")
    textPrint.unindent()
    textPrint.print(screen, f"Number of hats: {num_hats}")
    textPrint.indent()
    for i, hat in enumerate(values["hats"]):
        textPrint.print(screen, f"Hat {i} value: {hat}")
    textPrint.print(screen, "")

    # All of the code is copied except these lines underneath -> just a quick note for our controller
    # Thought about doing it in for loops with switch/case statement, but just manually did it
    textPrint.unindent()
    textPrint.unindent()
    textPrint.print(screen, "Key:")
    textPrint.indent()
    textPrint.print(screen, "Axes:")
    textPrint.indent()
    textPrint.print(screen, "Axis 0 = Left Joystick L/R")
    textPrint.print(screen, "Axis 1 = Left Joystick U/D")
    textPrint.print(screen, "Axis 2 = Left Trigger")
    textPrint.print(screen, "Axis 3 = Right Joystick L/R")
    textPrint.print(screen, "Axis 4 = Right Joystick U/D")
    textPrint.print(screen, "Axis 5 = Right Trigger")
    textPrint.unindent()
    textPrint.print(screen, "Buttons:")
    textPrint.indent()
    textPrint.print(screen, "Button 0 = A")
    textPrint.print(screen, "Button 1 = B")
    textPrint.print(screen, "Button 2 = X")
    textPrint.print(screen, "Button 3 = Y")
    textPrint.print(screen, "Button 4 = Left Bumper")
    textPrint.print(screen, "Button 5 = Right Bumper")
    textPrint.print(screen, "Button 6 = Back")
    textPrint.print(screen, "Button 7 = Start")
    textPrint.print(screen, "Button 8 = Logitech")
    textPrint.print(screen, "Button 9 = Left Stick In")
    textPrint.print(screen, "Button 10 = Right Stick In")
    textPrint.unindent()
    textPrint.print(screen, "Hats:")
    textPrint.indent()
    textPrint.print(screen, "Hat 0 = dpad")
    textPrint.indent()
    textPrint.print(
        screen, "(When the Mode button is pressed, the dpad and left Joystick swap:"
    )
    textPrint.print(screen, "Hat 0 Value becomes the left Joystick")
    textPrint.print(screen, "Axis Values 0-1 become the dpad)")
    textPrint.unindent()
    textPrint.unindent()
    textPrint.unindent()

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()


# controller loop
def main():
    pygame.init()

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Set the width and height of the screen [width,height]
    size = [500, 980]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Joystick Information")

    # Get ready to print
    textPrint = TextPrint()

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
                if joystick.get_button(1):  # 'X'
                    done = True
            if event.type == pygame.JOYBUTTONUP:
                print("Joystick button released.")

        values = update()
        show(screen, textPrint, values)

        # Limit to 20 frames per second
        clock.tick(20)


pygame.display.quit()


if __name__ == "__main__":
    main()
