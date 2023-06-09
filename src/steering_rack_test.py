import RPi.GPIO as GPIO
import drive_module as drive

#in this file I am workng on a better steering system. didnt like the old one. warning: the angle values are currently unclamped, ie if you tell it to do so,
# the motor will gladly attempt to turn farther than the steering rack physically is able to. reccomend limit degree range from [40,130] for now if you want to test
#-Chris 

# GPIO mode should be consistent across all modules
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Steering servo connected to pin GPIO 4
SERVO_PIN: int = 4
GPIO.setup(SERVO_PIN, GPIO.OUT)

# known calibration settings
#steer_cal_35 = {"freq": 35, "center": 2.4, "right": 4, "left": 1.2}
#steer_cal_35 = {"freq": 35, "center": 4.6, "right": 6.15, "left": 2.2}

class Steer:
    def __init__(self):
        self.pwm = GPIO.PWM(SERVO_PIN, 50) #set pwm frequency to 50 Hz on desired pin
        self.pwm.start(0)
    
    def func(self, angle: float=0):
        try:
            while (True):
                self.set_steering_angle(float(input("enter motor angle\n")))
        except KeyboardInterrupt:
            print("\nKeyBoardInterrupt. resetting to 0 and cleaning up.")
            self.pwm.ChangeDutyCycle(0)
            self.pwm.stop()
            GPIO.cleanup()

    def set_steering_angle(self, theta: float):
        
        dc = self.dc_from_degrees(theta)
        self.pwm.ChangeDutyCycle(dc)
    
    def dc_from_degrees(self,theta: float):
        #WARNING: the motor has 180 degree range of motion, but the steering rack does not. be careful.


        #duty cycle should range from 5% to 10%. ie, if f is the function from degrees to duty cycle (expressed as a percent),
        #f(0) = 5
        #f(90) = 7.5 
        #f(180) = 10

        #generalized: f(x) = x/36 + 5
        

        
        print(theta/36+5)
        return theta/36 + 5
    
    def set_dc(self,dc):
        try:
            while(True):
                
                self.pwm.ChangeDutyCycle(dc)
                print(dc)
        except KeyboardInterrupt:
            self.pwm.ChangeDutyCycle(0)
            self.pwm.stop()
            GPIO.cleanup()
        
        

if __name__ == "__main__":
    s = Steer()
    d = drive.Drive()
    #print(s.dc_from_degrees(90))
    d.forward()
    d.set(20)

    s.func()
    #dc=float(input("enter dc\n"))
    #s.set_dc(dc)

