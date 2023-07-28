"""
This module functions as an abstraction for the car via. the singleton class Car. It provides control over drive and steering rack motors, 
as well as some autonomous driving functionality.
"""

from constants import Drive_Params
from motor import DCMotor, Servo, cleanup

_SERVO_MOTOR_PIN         = 4
_DRIVE_MOTOR_POWER_PIN   = 25
_DRIVE_MOTOR_FORWARD_PIN = 6
_DRIVE_MOTOR_REVERSE_PIN = 5

steer_motor: Servo = Servo(_SERVO_MOTOR_PIN)
drive_motor: DCMotor = DCMotor(_DRIVE_MOTOR_POWER_PIN,_DRIVE_MOTOR_FORWARD_PIN,_DRIVE_MOTOR_REVERSE_PIN)

STEERING_RACK_CENTER = Drive_Params.STEERING_RACK_CENTER




class Car:
    _self = None

    """
    The car class controls driving and steering of the car. Should only instantiate once.
    """
    def __new__(cls):
        # Ensures only one instance of Car exists at one time. One machine shouldn't be controlling more than one car.
        if cls._self is None:
            cls._self = super().__new__(cls)
      
        return cls._self
        
    def __init__(self):
        """
        Create instance of car with initial steering angle at center position. Instantiates steering motor and drive motor at appropriate pins. Uses BCM pin numbering system.
        """

        self.current_steering_angle = 0
        self.current_drive_power = 0

        self.steer_motor: Servo = Servo(_SERVO_MOTOR_PIN)
        self.drive_motor: DCMotor = DCMotor(_DRIVE_MOTOR_POWER_PIN,_DRIVE_MOTOR_FORWARD_PIN,_DRIVE_MOTOR_REVERSE_PIN)
        self.jackknifed = False

    def gamepad_drive(self, trigger_val: int):
        """
        Input to this function must range from [-255, 255] where -255 is full reverse, 0 is stop, and 255 is full forward.
        Note that src.gamepad.get_trigger_values() maps [-255, 0] to left trigger, and [0,255] to right trigger
        """

        self.set_drive_power(trigger_val / 255)

    def set_drive_power(self, power: float):
        """
        Sets the drive power of the motor. Input should range from [-1, 1] where -1 is full reverse, 0 is stop, and 1 is full forward.
        """

        duty_cycle: int = int(abs(power * 100))
        if power < 0:
            self.drive_motor.reverse()
        elif power > 0:
            drive_motor.forward()
        else:
            drive_motor.stop_rotation()
        self.current_drive_power = power
        self.drive_motor.set_power(duty_cycle)

    def gamepad_steer(self, stick_val: float):
        """
        Input to this function must range from [-32768, 32767] where -32768 corresponds to full left, 0 to center, and 32767 to full right.
        This is the range of values provided by gamepad analog stick input.
        """
        JOYSTICK_MAX = 32767.0
        STEERIN_RACK_MAX = 21
        ANGLE_NORMALIZATION_CONSTANT = JOYSTICK_MAX / STEERIN_RACK_MAX # Ensures steering angle ranges from [-21, 21]
        angle = stick_val / ANGLE_NORMALIZATION_CONSTANT
        self.set_steering_angle(angle)

    def set_steering_angle(self, angle: float):
        """
        Inputs must range from [-21, 21]. Bad inputs will be clamped
        """

        LEFT_STEERING_RATIO, RIGHT_STEERING_RATIO = 21/60, 31/60
        

        if angle > 22: # goes up to 22 in case of rounding error
             angle = 21
        elif angle < -22: 
             angle = -21
        
        self.current_steering_angle = angle 
        
        angle = angle / LEFT_STEERING_RATIO if angle < 0 else angle / RIGHT_STEERING_RATIO
        self.steer_motor.set_angle(angle+STEERING_RACK_CENTER)


       

    
        


        

    
    def stabilize_steering_angle(
        self, 
        new_angle, 
        num_of_lane_lines, 
        max_angle_deviation_two_lines=40, 
        max_angle_deviation_one_line=40, 
    ):
        """
        Prevents some extreme input from resulting in an extreme steering reaction.
        Clamps steering angle based on previous steering angle.
        """
        if num_of_lane_lines == 2:
            max_angle_deviation = max_angle_deviation_two_lines
        else:
            max_angle_deviation = max_angle_deviation_one_line

        angle_deviation = new_angle - self.current_steering_angle
        if abs(angle_deviation) > max_angle_deviation:
            stabilized_steering_angle = int(
                self.current_steering_angle + 
                max_angle_deviation * angle_deviation / abs(angle_deviation)
            )
        else:
            stabilized_steering_angle = new_angle

        self.current_steering_angle = stabilized_steering_angle
        return stabilized_steering_angle

    def stop(self):
        """
        Stop steering and drive motors.
        """
        self.set_steering_angle(0)
        self.current_steering_angle = 0
        self.steer_motor.stop()
        self.drive_motor.stop()
    
    def cleanup(self):
        cleanup()






if __name__ == "__main__":
    from gamepad import Gamepad, Inputs
    g = Gamepad()
    car = Car()
    while True:
        g.update_input()
        if g.was_pressed(Inputs.R_BUMPER):
            car.set_steering_angle(car.current_steering_angle+1)
            print("angle:",car.current_steering_angle)   
        elif g.was_pressed(Inputs.L_BUMPER):
            car.set_steering_angle(car.current_steering_angle-1)
            print(car.current_steering_angle)   
        elif g.was_pressed(Inputs.B):
            break
