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
        io.set_PWM_dutycycle(self.power,0)

    def set(self, duty_cycle):
        io.set_PWM_dutycycle(self.power,duty_cycle)

class Servo:

    def __init__(self, pin:int,freq: int=FREQ):
        io.set_output(pin)
        self.pin: int = pin #may not be used
        self.freq = freq


    def start(self):
        self.pulse.start(0)
    
    def stop(self):
        self.set_pulse_width(0)

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

    
if __name__ == "__main__":
    print("dadsadawda")
    servo = Servo(4)
    theta = 50
    #servo.set_pulse_width(1500)
    print(servo.degrees_to_pulse_width(theta))
    io.stop()    