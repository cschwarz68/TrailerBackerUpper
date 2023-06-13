from motor import Servo 
from motor import DCMotor
from motor import cleanup
from gamepad import input, Gamepad as g, State




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
        duty_cycle = abs(power*50)
        if power < 0:
           drive_motor.reverse()
        elif power > 0:
           drive_motor.forward()
        else:
           drive_motor.park()

        drive_motor.set(duty_cycle)

def main():
    #steer_motor.start()
    drive_motor.stop_rotation()
    pulse = 90
    while 1:
        try:
            
            current_input = input()
            if current_input is not None:
                non_null_input = current_input

            
           
            #steer_motor.set_angle(pulse)

            
                
               
            if non_null_input[0]==g.R_TRIGGER:
                pulse = pulse + 0.3
            if non_null_input[0]==g.L_TRIGGER:
                pulse = pulse - 0.3
            
            

            if pulse <=0:
                    pulse = 0
            if pulse >= 180:
                pulse = 180

            print(pulse)
            steer_motor.set_angle(pulse)
            
           
            
        except KeyboardInterrupt:
            steer_motor.set_angle(90)
            return

#steering normalized from [-1,1]
def steer(normalized_val: float):
    pass


if __name__ == "__main__":
    main()
    cleanup()

