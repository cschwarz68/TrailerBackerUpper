from motor import Servo 
from motor import DCMotor
from motor import cleanup
from constants import Drive_Params

#This module functions as an abstraction for the car via the singleton class Car. It provides control over drive and steering rack motors,
#  as well as some autonomous driving functionality.



_SERVO_MOTOR_PIN = 4
_DRIVE_MOTOR_POWER_PIN = 25
_DRIVE_MOTOR_FORWARD_PIN = 6
_DRIVE_MOTOR_REVERSE_PIN = 5



steer_motor: Servo = Servo(_SERVO_MOTOR_PIN)
drive_motor: DCMotor = DCMotor(_DRIVE_MOTOR_POWER_PIN,_DRIVE_MOTOR_FORWARD_PIN,_DRIVE_MOTOR_REVERSE_PIN)


class Car:
    """The car class is a singleton class which controls driving and steering of the car."""
    
    def __new__(self):
        """create instance of car with initial steering angle at center position. Instantiates steering motor and drive motor at appropriate pins. Uses BCM pin numbering system."""

        self.current_steering_angle=0

        self.steer_motor: Servo = Servo(_SERVO_MOTOR_PIN)
        self.drive_motor: DCMotor = DCMotor(_DRIVE_MOTOR_POWER_PIN,_DRIVE_MOTOR_FORWARD_PIN,_DRIVE_MOTOR_REVERSE_PIN)

    
    def gamepad_drive(self,trigger_val):
        """Input to this function must range from [-255,255] where -255 is full reverse, 0 is stop, and 255 is full forward
        Note that trigger input falues from the inputs module range from [0,255] for each trigger."""

        self.set_drive_power(trigger_val/255)
        
    
    def set_drive_power(self,power):
        """Sets the drive power of the motor. input should range from [-1,1] where -1 is full reverse, 0 is stop, and 1 is full forward."""

        duty_cycle = abs(power*100)
        if power < 0:
            self.drive_motor.backwards()
        elif power > 0:
            drive_motor.forwards()
        else:
            drive_motor.stop_rotation()
        self.drive_motor.set(duty_cycle)

    
    def gamepad_steer(self,stick_val: float):
        """Input to this function must range from [-32768, 32767] where -32768 corresponds to full left, 0 to center, and 32767 to full right
        This is the range of values provided by gamepad analog stick input"""

        ANGLE_NORMALIZATION_CONSTANT = Drive_Params.JOYSTICK_MAX/90 #ensures steering angle ranges from [-90,90]
        angle = stick_val / ANGLE_NORMALIZATION_CONSTANT
        self.set_steering_angle(angle)
        
    
    def set_steering_angle(self, angle):
        """Sets angle of steering rack. Values outside of the bounds [constants.Drive_Params.STEERING_RACK_LEFT, constants.Drive_Params.STEERING_RACK_RIGHT] will be clamped to fit
        within the bounds. 0 is center, negative values are left, positive values are right"""

        angle = angle + Drive_Params.STEERING_RACK_CENTER
        angle = clamp_steering_angle(angle) #angle clamped to smaller bound than [-90,90] to ensure motor safety
        self.current_steering_angle = angle
        self.steer_motor.set_angle(angle)


    

    
    def stabilize_steering_angle(
    self,
    new_angle,
    num_of_lane_lines,
    max_angle_deviation_two_lines=45,
    max_angle_deviation_one_line=45,
    ):
        """legacy code, will document once i feel like reading it all"""

        if num_of_lane_lines == 2:
            max_angle_deviation = max_angle_deviation_two_lines
        else:
            max_angle_deviation = max_angle_deviation_one_line

        angle_deviation = new_angle - self.current_steering_angle
        if abs(angle_deviation) > max_angle_deviation:
            stabilized_steering_angle = int(
                self.current_steering_angle
                + max_angle_deviation * angle_deviation / abs(angle_deviation)
            )
        else:
            stabilized_steering_angle = new_angle

        self.current_steering_angle = stabilized_steering_angle
        return stabilized_steering_angle -90 #subtracting 90 because this is old code from the system where angle range was [0,180]; it is now [-90,90]

    
    def stop(self):
        """stop steering and drive motors"""

        self.steer_motor.stop()
        self.drive_motor.stop()


def clamp_steering_angle(angle):
    """ensures angles supplied to motor do not exceed bounds set in constants.Drive_Params"""

    angle = Drive_Params.STEERING_RACK_RIGHT if angle >= Drive_Params.STEERING_RACK_RIGHT else angle
    angle = Drive_Params.STEERING_RACK_LEFT if angle <= Drive_Params.STEERING_RACK_LEFT else angle
    return angle


