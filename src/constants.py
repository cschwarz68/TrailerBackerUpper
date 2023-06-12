from enum import Enum

class Main_Mode(Enum):
    MANUAL       = 0
    AUTO_FORWARD = 1
    AUTO_REVERSE = 2

class Drive_Params():
    JOYSTICK_MAX = 32767.0
    TURN_STRAIGHT = 90

class Lane_Bounds_Ratio(Enum):
    LEFT  = 2 / 3
    RIGHT = 1 / 3
