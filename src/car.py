from motor import Servo 
from motor import DCMotor
from motor import cleanup
from gamepad import Inputs as i, State, Gamepad
from constants import Drive_Params





_SERVO_MOTOR_PIN = 4
_DRIVE_MOTOR_POWER_PIN = 25
_DRIVE_MOTOR_FORWARD_PIN = 6
_DRIVE_MOTOR_REVERSE_PIN = 5



steer_motor: Servo = Servo(_SERVO_MOTOR_PIN)
drive_motor: DCMotor = DCMotor(_DRIVE_MOTOR_POWER_PIN,_DRIVE_MOTOR_FORWARD_PIN,_DRIVE_MOTOR_REVERSE_PIN)

class Car:

    def __init__(self):
        self.current_steering_angle=0

        self.steer_motor: Servo = Servo(_SERVO_MOTOR_PIN)
        self.drive_motor: DCMotor = DCMotor(_DRIVE_MOTOR_POWER_PIN,_DRIVE_MOTOR_FORWARD_PIN,_DRIVE_MOTOR_REVERSE_PIN)

    #Input to this function must range from [-255,255] where -255 is full reverse, 0 is stop, and 255 is full forward
    #This is the range of values provided by gamepad analog trigger input
    def gamepad_drive(self,trigger_val):
        self.set_drive_power(trigger_val/255)
        
    
    def set_drive_power(self,power):
        duty_cycle = abs(power*100)
        if power < 0:
            self.drive_motor.backwards()
        elif power > 0:
            drive_motor.forwards()
        else:
            drive_motor.stop_rotation()
        self.drive_motor.set(duty_cycle)

    #Input to this function must range from [-32768, 32767] where -32768 corresponds to full left, 0 to center, and 32767 to full right
    #This is the range of values provided by gamepad analog stick input
    def gamepad_steer(self,stick_val: float):
        ANGLE_NORMALIZATION_CONSTANT = Drive_Params.JOYSTICK_MAX/90 #ensures steering angle ranges from [-90,90]
        angle = stick_val / ANGLE_NORMALIZATION_CONSTANT
        self.set_steering_angle(stick_val)
        
    
    def set_steering_angle(self, angle):
        angle = angle + Drive_Params.STEERING_RACK_CENTER
        angle = clamp_steering_angle(angle) #angle clamped to smaller bound than [-90,90] to ensure motor safety
        self.current_steering_angle = angle
        self.steer_motor.set_angle(angle)


    

    #legacy code, will document once i feel like reading it all
    def stabilize_steering_angle(
    self,
    new_angle,
    num_of_lane_lines,
    max_angle_deviation_two_lines=45,
    max_angle_deviation_one_line=45,
    ):
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
        self.steer_motor.stop()
        self.drive_motor.stop()



def clamp_steering_angle(angle):
    angle = Drive_Params.STEERING_RACK_RIGHT if angle >= Drive_Params.STEERING_RACK_RIGHT else angle
    angle = Drive_Params.STEERING_RACK_LEFT if angle <= Drive_Params.STEERING_RACK_LEFT else angle
    return angle


def main():
    #steer_motor.start()
    car = Car()
    g = Gamepad()

    car.drive_motor.stop_rotation()
    steering_angle = 0
    trigger_val = 0
    while 1:
        try:
            g.update_input()
            print(steering_angle)
            # current_input = input()
            # if current_input is not None:
            #     non_null_input = current_input

            
           
            #steer_motor.set_angle(pulse)

            
                
            stick_val = g.get_abs_value(i.LX)
            if stick_val is not None:
                steering_angle = stick_val
         
            r_trigger_val = g.get_abs_value(i.R_TRIGGER)
            if r_trigger_val is not None:
                trigger_val = r_trigger_val
                
            l_trigger_val = g.get_abs_value(i.L_TRIGGER)
            if l_trigger_val is not None:
                trigger_val = -l_trigger_val

            
            car.gamepad_drive(trigger_val)
            car.gamepad_steer(steering_angle)
            
           
            
        except KeyboardInterrupt:
            steer_motor.set_angle(90)
            return
        





if __name__ == "__main__":
    main()
    cleanup()

