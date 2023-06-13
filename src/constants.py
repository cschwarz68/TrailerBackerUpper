from enum import Enum

class Main_Mode(Enum):
    MANUAL       = 0
    AUTO_FORWARD = 1
    AUTO_REVERSE = 2

class Drive_Params():
    JOYSTICK_MAX = 32767.0
    TURN_STRAIGHT = 90
    STEERING_RACK_CENTER = 82.5
    STEERING_RACK_RIGHT = 130
    STEERING_RACK_LEFT = 40
