from enum import Enum

class Main_Mode(Enum):
    MANUAL       = 0
    AUTO_FORWARD = 1
    AUTO_REVERSE = 2

class Drive_Params():
    JOYSTICK_MAX = 32767.0
    TURN_STRAIGHT = 90
    SHARP_TURN_DEGREES = 7.5

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
    CAMERA_MID_OFFSET_PERCENT = 0.02

class Camera_Settings():
    # "The alpha channel (also called alpha planes) is a color component 
    # that represents the degree of transparency (or opacity) of a color (i.e., the red, green and blue channels). 
    # It is used to determine how a pixel is rendered when blended with another."
    PREVIEW_CONFIG_FORMAT = "YUV420" # This is a color model different from RGB.
    RESOLUTION            = (640, 480)
    FRAMERATE             = 60
    ALPHA                 = 20
