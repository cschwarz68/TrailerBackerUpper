from enum import Enum
import yaml

def read_yaml(filename):
    with open(f'{filename}.yml','r') as f:
        output = yaml.safe_load(f)
    return output
    

config = read_yaml('../TrailerBackerUpper/config')
del yaml

settings = config['settings']

driving = settings['driving']

steering = settings['steering rack']

camera = settings['camera']

streaming = settings['streaming']

class Main_Mode(Enum):
    MANUAL       = 0
    AUTO_FORWARD = 1
    AUTO_REVERSE = 2
    STOPPED = 3

class Drive_Params:
    STEERING_RACK_CENTER       = steering["center"]

   
    SHARP_TURN_DEGREES         = driving["sharp turn threshold"]
    SHARP_TURN_DEGREES_REVERSE = driving["sharp turn reverse threshold"]

class Lane_Bounds_Ratio:
    LEFT  = 3 / 4
    RIGHT = 1 / 4

class Image_Processing_Calibrations:
    """
    IMPORTANT

    =0% --> Camera is exactly in the middle.
    >0% --> Camera is skewed towards the left.
    <0% --> Camera is skewed towards the right.

    Must be expressed as decimal. 2% -> .02

    This is the original comment from the prior developer:
        "0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right"
    """
    CAMERA_MID_OFFSET_PERCENT = camera["rear offset"] 

class Camera_Settings():
    # I do not think we use this at all

    
    # "The alpha channel (also called alpha planes) is a color component 
    # that represents the degree of transparency (or opacity) of a color (i.e., the red, green and blue channels). 
    # It is used to determine how a pixel is rendered when blended with another."
    PREVIEW_CONFIG_FORMAT = "YUV420" # This is a color model different from RGB.
    RESOLUTION            = (640, 480)
    FRAMERATE             = 60
    ALPHA                 = 20

class OpenCV_Settings:
    RECORDING_FRAMERATE = camera["framerate"] # Arbitrary (this number does affect the frame rate, but the number you put here is not the true framerate and we don't know why).

class Reverse_Calibrations:
    POSITION_THRESHOLD         = driving["position threshold"]
    ANGLE_OFF_CENTER_THRESHOLD = driving["trailer angle off center threshold"]
    HITCH_ANGLE_THRESHOLD      = driving["hitch angle threshold"]
    TURN_RATIO                 = driving["turn ratio"]

class Streaming:
    DESTINATION_ADDRESS = streaming["destination ip"]
    DESTINATION_PORT    = streaming["destination port"]
    ENABLED             = streaming["enabled"]

if __name__ == "__main__":
    print(settings)