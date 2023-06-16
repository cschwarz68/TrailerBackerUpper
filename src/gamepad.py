from inputs import get_gamepad

_STICK_MAX_VALUE = 32768

_INPUTS = [
        ("Key",      "BTN_EAST"), 
        ("Key",      "BTN_SOUTH"), 
        ("Key",      "BTN_WEST"), 
        ("Key",      "BTN_NORTH"), 
        ("Key",      "BTN_START"), 
        ("Key",      "BTN_SELECT"),
        ("Absolute", "ABS_RX"),
        ("Absolute", "ABS_RY"), 
        ("Absolute", "ABS_Y"),
        ("Absolute", "ABS_X")
    ]

class Inputs:
    SYN_REPORT = 0
    # Buttons
    A = 1
    B = 2
    X = 3
    Y = 4
    R_BUMPER = 5
    L_BUMPER = 6
    START = 7
    SELECT = 8
    # Sticks
    RY = 9
    RX = 10
    LY = 11
    LX = 12
    # Triggers
    R_TRIGGER = 13
    L_TRIGGER = 14
    D_PAD_Y = 15
    D_PAD_X = 16

class State:
    # Constants for input state.
    PRESSED = 1
    RELEASED = 0

    LEFT = -1
    UP = -1
    DOWN = 1
    RIGHT = 1

_KEYMAP = {
    "BTN_SOUTH": Inputs.A, 
    "BTN_EAST": Inputs.B, 
    "SYN_REPORT": Inputs.SYN_REPORT, 
    "BTN_NORTH": Inputs.X, 
    "BTN_WEST": Inputs.Y, 
    "BTN_START": Inputs.START, 
    "BTN_SELECT": Inputs.SELECT, 
    "BTN_TR": Inputs.R_BUMPER, 
    "BTN_TL": Inputs.L_BUMPER, 
    "ABS_RZ": Inputs.R_TRIGGER, 
    "ABS_Z": Inputs.L_TRIGGER, 
    "ABS_RX": Inputs.RX, 
    "ABS_RY": Inputs.RY, 
    "ABS_Y": Inputs.LY, 
    "ABS_X": Inputs.LX, 
    "ABS_HAT0Y": Inputs.D_PAD_Y, 
    "ABS_HAT0X": Inputs.D_PAD_X, 
    "SYN_REPORT": Inputs.SYN_REPORT
}

class Gamepad:
    """
    Gamepad abstractions.
    """

    def __init__(self):
        self.input = None

    def update_input(self):
        events = get_gamepad()
        for event in events:
            self.input =(_KEYMAP[event.code],event.state)
            return self.input

    def was_pressed(self, button:int) -> bool:
        if button not in range(1,9): # Appropriate range of buttons in Gamepad class above.
            raise Exception("Invalid button! See gamepad.Gamepad!")
        elif self.input is not None:
            return (self.input[0] == button) and (self.input[1] == State.PRESSED)

    def get_stick_value(self, stick_axis: int) -> int:
        if stick_axis not in range (9, 13):
            raise Exception("Invalid stick input! See gamepad.Gamepad!")
        elif self.input is not None:
            if self.input[0] == stick_axis:
                return self.input[1]
            
    def get_trigger_value(self) -> int:
        if self.input is not None:
            if self.input[0] == Inputs.R_TRIGGER:
                    return self.input[1]
            elif self.input[0] == Inputs.L_TRIGGER:
                    return -self.input[1]

if __name__ == "__main__":
    while True:
        events = get_gamepad()
        for event in events:
            print(event.ev_type, event.code, event.state)
