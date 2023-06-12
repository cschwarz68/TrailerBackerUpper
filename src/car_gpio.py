import RPi.GPIO as GPIO

OUT = GPIO.OUT
IN = GPIO.IN

def cleanup():
    GPIO.cleanup()

class Servo:

    def __init__(self, pin:int, freq: int=50):
        self.pin: int = pin
        self.freq = freq
        self.pulse = GPIO.PWM(pin,freq)

    def start(self):
        self.PWM.start(0)
    
    def stop(self):
        self.PWM.stop()

    def set_duty_cycle(self, duty_cycle):
        self.pwm.ChangeDutyCycle(duty_cycle)
    
    def set_angle(self, theta):
        duty_cycle = self.__degrees_to_duty_cycle(theta)
        self.set_duty_cycle(duty_cycle)

    def __degrees_to_duty_cycle(self,theta):
        #WARNING: the motor has 180 degree range of motion, but the steering rack does not. be careful.


        #duty cycle should range from 5% to 10%. ie, if f is the function from degrees to duty cycle (expressed as a percent),
        #f(0) = 5
        #f(90) = 7.5 
        #f(180) = 10

        #generalized: f(x) = x/36 + 5
        

        #TODO: this is currently only for frequencey of 50 degrees; will generalize later
        print(theta/36+5)
        return theta/36 + 5


    



