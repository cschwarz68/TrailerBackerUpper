from inputs import get_gamepad
from enum import Enum

_STICK_MAX_VALUE = 32768



_INPUTS = [
        ("Key", "BTN_EAST"), 
        ("Key", "BTN_SOUTH"), 
        ("Key", "BTN_WEST"), 
        ("Key", "BTN_NORTH"), 
        ("Key", "BTN_START"), 
        ("Key","BTN_SELECT"),
        ("Absolute", "ABS_RX"),
        ("Absolute","ABS_RY"), 
        ("Absolute", "ABS_Y"),
        ("Absolute", "ABS_X")
    ]

class Inputs():
    #enum part
    SYN_REPORT=0
    #buttons
    A = 1
    B = 2
    X = 3
    Y=4
    R_BUMPER=5
    L_BUMPER=6
    START = 7
    SELECT=8
    #absolute
    RY=9
    RX=10
    LY=11
    LX=12
    R_TRIGGER=13
    L_TRIGGER = 14
    D_PAD_Y = 15
    D_PAD_X = 16

class State:
    #constants for input state
    PRESSED = 1
    RELEASED = 0

    LEFT = -1
    UP = -1
    DOWN = 1
    RIGHT = 1

   

    



_keymap = {
    "BTN_SOUTH": Inputs.A,
    "BTN_EAST"  : Inputs.B,
    "SYN_REPORT" : Inputs.SYN_REPORT,
    "BTN_NORTH" : Inputs.X,
    "BTN_WEST" : Inputs.Y,
    "BTN_START" : Inputs.START,
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
    "ABS_HAT0X":Inputs.D_PAD_X,
    "SYN_REPORT":Inputs.SYN_REPORT
}


class Gamepad:
    
# def pressed() -> dict[str, dict[str, int]]:
    
#     ret = dict()
#     events = get_gamepad()
#     for key in _INPUTS:
#         if key[0] not in ret:
#             ret[key[0]] = dict()
#         ret[key[0]][key[1]] = None
#     for event in events:
#         # print(event.ev_type, event.code, event.state) # For debugging.
#         if event.ev_type in ret and event.code in ret[event.ev_type]:
#             ret[event.ev_type][event.code] = event.state
#     return ret

    def __init__(self):
        self.input = None

    def update_input(self):
        events = get_gamepad()
        for event in events:
            self.input =(_keymap[event.code],event.state)
            return self.input
           
                
            

    #this idea was stupid

 

    def was_pressed(self, button:int) -> bool:
        if button not in range(1,9): #appropriate range of buttons in Gamepad class above
            raise Exception("Invalid button! See gamepad.Gamepad!")
        elif self.input is not None:
            return (self.input[0]==button) and (self.input[1]==State.PRESSED)

    def get_stick_value(self, stick_axis: int):
        if stick_axis not in range (9,13):
            raise Exception("Invalid stick input! See gamepad.Gamepad!")
        elif self.input is not None:
            if self.input[0]==stick_axis:
                return self.input[1]
            
    def get_trigger_value(self):
        if self.input is not None:
            if self.input[0] == Inputs.R_TRIGGER:
                    return self.input[1]
            elif self.input[0] == Inputs.L_TRIGGER:
                    return -self.input[1]


            

# def b_pressed() -> bool:
#     return pressed()["Key"]["BTN_EAST"] == 1

# def x_pressed() -> bool:
#     return pressed()["Key"]["BTN_NORTH"] == 1

# def y_pressed() -> bool:
#     return pressed()["Key"]["BTN_WEST"] == 1

# def start_pressed() -> bool:
#     return pressed()["Key"]["BTN_SOUTH"] == 1

# def select_pressed() -> bool:
#     return pressed()["Key"]["BTN_SELECT"] == 1

# def get_RX():
#     return pressed()["Absolute"]["ABS_RX"]

def normalize_stick_inputs(x):
    if x is None:
        return None
    return x/_STICK_MAX_VALUE






if __name__ == "__main__":
    while 1:
        events = get_gamepad()
        for event in events:
            print(event.ev_type, event.code, event.state)


