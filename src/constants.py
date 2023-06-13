from enum import Enum

class Main_Mode(Enum):
    MANUAL       = 0
    AUTO_FORWARD = 1
    AUTO_REVERSE = 2

class Drive_Params():
    JOYSTICK_MAX = 32767.0
    TURN_STRAIGHT = 90

class Lane_Bounds_Ratio():
    LEFT  = 2 / 3
    RIGHT = 1 / 3

class Image_Processing_Calibrations():
    """
    IMPORTANT

    =0% --> Camera is exactly in the middle.
    >0% --> Camera is skewed towards the left.
    <0% --> Camera is skewed towards the right.

    This is the original comment from the prior developer:
        "0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right"
    """
    camera_mid_offset_percent = 0.02
