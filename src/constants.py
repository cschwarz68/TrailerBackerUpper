from enum import Enum
import yaml

"""
This module stores constants used throughout the project. The majority of these constants can be configured via `config.yml`.
Descriptions of these constants can be found in the config file as well.
"""

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

gpio = settings['gpio']

class MainMode(Enum):
    """
    Enumeration for the different driving modes
    """
    MANUAL       = 0
    AUTO_FORWARD = 1
    AUTO_REVERSE = 2
    STOPPED = 3

class DriveParams:
    STEERING_RACK_CENTER       = steering["center"]

    SHARP_TURN_DEGREES         = driving["sharp turn threshold"]
    
    SHARP_TURN_DEGREES_REVERSE = driving["sharp turn reverse threshold"]

class LaneBoundsRatio:
    LEFT  = 1 / 2
    RIGHT = 1 / 2

class GPIO:
    SERVO_MOTOR_PIN         = gpio["servo motor"]
    DRIVE_MOTOR_POWER_PIN   = gpio["drive motor power"]
    DRIVE_MOTOR_FORWARD_PIN = gpio["drive motor forward"]
    DRIVE_MOTOR_REVERSE_PIN = gpio["drive motor reverse"]


class ImageProcessingCalibrations:
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

class CameraSettings:

    RESOLUTION: tuple[int, int] = (camera["resolution width"], camera["resolution height"])
    FRAMERATE: int              = camera["framerate"]


class OpenCVSettings:
    RECORDING_FRAMERATE: int = camera["framerate"] # Arbitrary (this number does affect the frame rate, but the number you put here is not the true framerate and we don't know why).

class ReverseCalibrations:
    POSITION_THRESHOLD         = driving["position threshold"]
    ANGLE_OFF_CENTER_THRESHOLD = driving["trailer angle off center threshold"]
    HITCH_ANGLE_THRESHOLD      = driving["hitch angle threshold"]
    TURN_RATIO                 = driving["turn ratio"]

class Streaming:
    DESTINATION_ADDRESS = streaming["destination ip"]
    DESTINATION_PORT    = streaming["destination port"]
    ENABLED: bool             = streaming["enabled"]
    WEB_STREAMING       = streaming["web streaming"]

if __name__ == "__main__":
    print(settings)