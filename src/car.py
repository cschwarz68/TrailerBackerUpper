from motor import Servo 
from motor import DCMotor
from motor import cleanup
from gamepad import input, Gamepad as g, State
from constants import Drive_Params




_SERVO_MOTOR_PIN = 4
_DRIVE_MOTOR_POWER_PIN = 25
_DRIVE_MOTOR_FORWARD_PIN = 6
_DRIVE_MOTOR_REVERSE_PIN = 5

LEFT_STEERING_RACK_BOUND= 0
RIGHT_STEERING_RACK_BOUND = 0

steer_motor: Servo = Servo(_SERVO_MOTOR_PIN)
drive_motor: DCMotor = DCMotor(_DRIVE_MOTOR_POWER_PIN,_DRIVE_MOTOR_FORWARD_PIN,_DRIVE_MOTOR_REVERSE_PIN)

def manual_driving():
    pass 

def set_steering_angle(theta):
    steer_motor.set_angle(theta)

def set_center_pos(angle: int):
    pass

def drive(power):
        # Normalized driving. 1 is full speed forward, -1 is full speed reverse.
              # Normalized driving. 1 is full speed forward, -1 is full speed reverse.
        duty_cycle = abs(power*100)
        if power < 0:
           drive_motor.backwards()
        elif power > 0:
           drive_motor.forwards()
        else:
           drive_motor.stop_rotation()

        drive_motor.set(duty_cycle)

def main():
    #steer_motor.start()
    drive_motor.stop_rotation()
    pulse = 90
    while 1:
        try:
            print(pulse)
            current_input = input()
            if current_input is not None:
                non_null_input = current_input

            
           
            #steer_motor.set_angle(pulse)

            
                
               
            if non_null_input[0]==g.R_TRIGGER:
                pulse = pulse + 0.3
            if non_null_input[0]==g.L_TRIGGER:
                pulse = pulse - 0.3

            if non_null_input[0]==g.LY:
                stick_val = non_null_input[1]
                drive(-stick_val/Drive_Params.JOYSTICK_MAX)
            
            

            steer(pulse)
            
           
            
        except KeyboardInterrupt:
            steer_motor.set_angle(90)
            return
        
def clamp_steering_angle(angle):
    angle = Drive_Params.STEERING_RACK_RIGHT if angle >= Drive_Params.STEERING_RACK_RIGHT else angle
    angle = Drive_Params.STEERING_RACK_LEFT if angle <= Drive_Params.STEERING_RACK_LEFT else angle
    return angle

#steering normalized such that 0 is center, negative values go left, positive values go right
#exact bounds can be found in constants.Drive_Params
def steer(angle: float):
    angle = angle + Drive_Params.STEERING_RACK_CENTER
    angle = clamp_steering_angle(angle)
    steer_motor.set_angle(angle)
    

def drive(power):
 # Normalized driving. 1 is full speed forward, -1 is full speed reverse.
             
        duty_cycle = abs(power*100)
        if power < 0:
           drive_motor.backwards()
        elif power > 0:
           drive_motor.forwards()
        else:
           drive_motor.stop_rotation()

        drive_motor.set(duty_cycle)


if __name__ == "__main__":
    main()
    cleanup()

