import gpio as io
#Abstractions of servos and DC motors


class DCMotor:
    STOP = 0
    FORWARD = 1
    REVERSE = -1
    def __init__(self, power: int, forward: int, reverse: int, duty_cycle: int = 50):
        

        self.power = power 
        self.forward = forward
        self.reverse = reverse 

        io.setup_output(power)
        io.setup_output(forward)
        io.setup_output(reverse)

        self.duty_cycle = duty_cycle
        self.pulse = io.start_pwm(power)

    def forwards(self):
        io.set_low(self.reverse)
        io.set_high(self.forward)
    
    def backwards(self):
        io.set_low(self.forward)
        io.set_high(self.reverse)
    
    def stop_rotation(self):
        io.set_low(self.forward)
        io.set_low(self.reverse)

    def stop(self):
        self.pulse.stop()

class Servo:

    def __init__(self, pin:int,freq: int=50):
        io.setup_output(pin)
        self.pin: int = pin #may not be used
        self.freq = freq
        self.pulse = io.start_pwm(pin)

    def start(self):
        self.pulse.start(0)
    
    def stop(self):
        self.pulse.stop()

    def set_duty_cycle(self, duty_cycle):
        self.pulse.ChangeDutyCycle(duty_cycle)
    
    def set_angle(self, theta: float):
        duty_cycle = self.__degrees_to_duty_cycle(theta)
        self.set_duty_cycle(duty_cycle)

    def __degrees_to_duty_cycle(self,theta: float) -> float:
        #WARNING: the motor has 180 degree range of motion, but the steering rack does not. be careful.


        #duty cycle should range from 5% to 10%. ie, if f is the function from degrees to duty cycle (expressed as a percent),
        #f(0) = 5
        #f(90) = 7.5 
        #f(180) = 10

        #generalized: f(x) = x/36 + 5
        

        #TODO: this is currently only for frequencey of 50 Hz (period 20 ms); will generalize later
        print(theta/36+5)
        return theta/36 + 5
