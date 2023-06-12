from motor import Servo 
from motor import DCMotor
from gamepad import input, Key, PRESSED, RELEASED
import gpio



_SERVO_MOTOR_PIN = 4
_DRIVE_MOTOR_POWER_PIN = 25
_DRIVE_MOTOR_FORWARD_PIN = 6
_DRIVE_MOTOR_REVERSE_PIN = 5

gpio.set_mode(gpio.BCM)
steer_motor: Servo = Servo(4)
drive_motor: DCMotor = DCMotor(_DRIVE_MOTOR_POWER_PIN,_DRIVE_MOTOR_FORWARD_PIN,_DRIVE_MOTOR_REVERSE_PIN)

def manual_driving():
    pass 

def set_steering_angle(theta):
    steer_motor.set_angle(theta)

def main():
    steer_motor.start()
    angle = 60
    while 1:
        try:
            key = input()
            if key==(Key.A,RELEASED):
                 angle = angle - 5
                 print(angle)
            if key==(Key.B,RELEASED):
                angle = angle+5
                print(angle)
            
           
            steer_motor.set_angle(angle)
        except KeyboardInterrupt:
            steer_motor.stop()
            return

        


if __name__ == "__main__":
    main()
    gpio.cleanup()

