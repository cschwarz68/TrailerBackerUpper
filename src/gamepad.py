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

class Gamepad():
    #enum part
    SYN_REPORT=0
    A = 1
    B = 2
    X = 3
    Y=4
    RY=5
    RX=6
    LY=7
    LX=8
    R_BUMPER=10
    L_BUMPER=11
    START = 12
    SELECT=13
    R_TRIGGER=14
    L_TRIGGER = 15
    D_PAD_Y = 16
    D_PAD_X = 17

class State:
    #constants for input state
    PRESSED = 1
    RELEASED = 0

    LEFT = -1
    UP = -1
    DOWN = 1
    RIGHT = 1

   

    



_keymap = {
    "BTN_SOUTH": Gamepad.A,
    "BTN_EAST"  : Gamepad.B,
    "SYN_REPORT" : Gamepad.SYN_REPORT,
    "BTN_NORTH" : Gamepad.X,
    "BTN_WEST" : Gamepad.Y,
    "BTN_START" : Gamepad.START,
    "BTN_SELECT": Gamepad.SELECT,
    "BTN_TR": Gamepad.R_BUMPER,
    "BTN_LR": Gamepad.L_BUMPER,
    "ABS_RZ": Gamepad.R_TRIGGER,
    "ABS_Z": Gamepad.L_TRIGGER,
    "ABS_RX": Gamepad.RX,
    "ABS_RY": Gamepad.RY,
    "ABS_Y": Gamepad.LY,
    "ABS_X": Gamepad.LX,
    "ABS_HAT0Y": Gamepad.D_PAD_Y,
    "ABS_HAT0X":Gamepad.D_PAD_X
    
}



def pressed() -> dict[str, dict[str, int]]:
    
    ret = dict()
    events = get_gamepad()
    for key in _INPUTS:
        if key[0] not in ret:
            ret[key[0]] = dict()
        ret[key[0]][key[1]] = None
    for event in events:
        # print(event.ev_type, event.code, event.state) # For debugging.
        if event.ev_type in ret and event.code in ret[event.ev_type]:
            ret[event.ev_type][event.code] = event.state
    return ret

def input():
    events = get_gamepad()
    for event in events:
        if(event.ev_type=="Key"):
            return (_keymap[event.code],event.state)
        elif(event.ev_type=="Absolute"):
            return (_keymap[event.code],event.state)#why did I write this as two separate conditions???
        

#this idea was stupid

# def a_pressed() -> bool:
#     return pressed()["Key"]["BTN_SOUTH"] == 1

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



def main():
    
   
    while 1:
      #val = get_RX()
      print(input())
      
def print_back_inputs():
    while 1:
        events = get_gamepad()
        for event in events:
            print(event.ev_type, event.code, event.state)

if __name__ == "__main__":
    print_back_inputs()
    #main()





def manual(events):
    global done, steer, drive, mode, transition_mode
    """
    This commented code uses the is_pressed function.
    Use in case get_pressed is buggy.
    """
    # if is_pressed(events, "Key", "BTN_EAST", 1)[0]:
        # done = True
    # elif is_pressed(events, "Key", "BTN_SOUTH", 1)[0]:
        # pass # Bypassing functionality for now.
        # video_capture()
    # event_x = is_pressed(events, "Absolute", "ABS_RX", None)[1] # RX refers to the right joystick.
    # event_y = is_pressed(events, "Absolute", "ABS_Y", None)[1]
    # if event_x is not None:
    #     x = float(event_x.state) / Drive_Params.TURN_MAX
    #     steer.steer(x)
    # if event_y is not None:
    #     y = float(event_y.state) / Drive_Params.TURN_MAX
    #     drive.drive(-y)
    """
    IMPORTANT

    On the controller:

            Y                  West
          X + B    -->    North + East
            A                 South
    """
    # pressed = get_pressed(events, [
    #     ("Key", "BTN_EAST"), 
    #     ("Key", "BTN_SOUTH"), 
    #     ("Key", "BTN_WEST"), 
    #     ("Key", "BTN_NORTH"), 
    #     ("Key", "BTN_START"), 
    #     ("Absolute", "ABS_RX"), 
    #     ("Absolute", "ABS_Y")
    # ])
    # if pressed["Key"]["BTN_EAST"] == 1:
    #     done = True
    # elif pressed["Key"]["BTN_SOUTH"] == 1:
    #     pass # Bypassing functionality for now.
    #     # video_capture()
    # elif pressed["Key"]["BTN_NORTH"] == 1:
    #     transition_mode = Main_Mode.AUTO_FORWARD
    #     print("Transitioned to auto FORWARD. Press START to init.")
    # elif pressed["Key"]["BTN_WEST"] == 1:
    #     transition_mode = Main_Mode.AUTO_REVERSE
    #     print("Transitioned to auto REVERESE. Press START to init.")
    # elif pressed["Key"]["BTN_START"] == 1:
    #     print("Entered Mode:", transition_mode)
    #     mode = transition_mode
    # x = pressed["Absolute"]["ABS_RX"]
    # y = pressed["Absolute"]["ABS_Y"]
    # if x is not None:
    #     steer.steer(x / Drive_Params.JOYSTICK_MAX)
    # if y is not None:
    #     drive.drive(-y / Drive_Params.JOYSTICK_MAX)
