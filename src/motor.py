import gpio as io


#This module provides abstractions of servos and DC motors

io = io.IO()
io.set_PWM_range(9,100) #makes it so 50 = 50% duty cycle

FREQ = 50 #default PWM frequency

def cleanup():
    io.stop()

class DCMotor:
    STOP = 0
    FORWARD = 1
    REVERSE = -1
    

    def __init__(self, power: int, forward: int, reverse: int, duty_cycle: int = 50):
        

        self.power = power 
        self.forward = forward
        self.reverse = reverse 

        io.set_PWM_frequency(power,FREQ)
        io.set_PWM_frequency(forward, FREQ)
        io.set_PWM_frequency(reverse, FREQ)

        io.set_output(power)
        io.set_output(forward)
        io.set_output(reverse)

        self.duty_cycle = duty_cycle
        #self.pulse = io.start_pwm(power)
        #io.set_PWM_dutycycle(duty_cycle)

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
        io.set_PWM_dutycycle(0)

class Servo:

    def __init__(self, pin:int,freq: int=FREQ):
        io.set_output(pin)
        self.pin: int = pin #may not be used
        self.freq = freq


    def start(self):
        self.pulse.start(0)
    
    def stop(self):
        self.pulse.stop()

    def set_duty_cycle(self, duty_cycle):
        self.pulse.ChangeDutyCycle(duty_cycle)
    
    def set_angle(self, theta: float):
        width = self.degrees_to_pulse_width(theta)
        self.set_pulse_width(width)

    def degrees_to_pulse_width(self, theta: float):
        pulse = theta*100/9 + 500
        return int(pulse)

    '''
    0 -> off
    1000 -> full counterclockwise
    1500 -> center
    2000 -> full clockwise
    '''
    def set_pulse_width(self,width: int):
        io.set_servo_pulsewidth(self.pin,width)

    def __degrees_to_duty_cycle(self,theta: float) -> float:
        #WARNING: the motor has 180 degree range of motion, but the steering rack does not. be careful.


        #duty cycle should range from 5% to 10%. ie, if f is the function from degrees to duty cycle (expressed as a percent),
        #f(0) = 5
        #f(90) = 7.5 
        #f(180) = 10

        #generalized: f(x) = x/36 + 5
        

        #TODO: this is currently only for frequencey of 50 Hz (period 20 ms); will generalize later
        #print(theta/36+5)
        return theta/36 + 5
if __name__ == "__main__":
    print("dadsadawda")
    servo = Servo(4)
    theta = 50
    #servo.set_pulse_width(1500)
    print(servo.degrees_to_pulse_width(theta))
    io.stop()    