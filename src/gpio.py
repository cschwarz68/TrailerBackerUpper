import RPi.GPIO as GPIO
#THIS MODULE IS NOT READY FOR USE
BCM = GPIO.BCM
BOARD = GPIO.BOARD
OUT = GPIO.OUT
IN = GPIO.IN



#Set GPIO pin numbering system. Default: BCM
def set_mode(mode=BCM):
    if (mode != BCM) or (mode != BCM):
        raise ValueError("Pin mode must be BCM or BOARD")
    else:
        GPIO.setmode(mode)

def setup_output(pin: int):
    GPIO.setup(pin, GPIO.OUT)

#is this needed? could I just make setup only set as output?
def setup_input(pin:int):
    GPIO.setup(pin, GPIO.IN)
  
def set_low(pin: int):
    GPIO.output(pin,GPIO.LOW)

def set_high(pin: int):
    GPIO.output(pin,GPIO.HIGH)

def cleanup():
    GPIO.cleanup()

# def set_pin_out(pin: int):
#     GPIO.set(pin, GPIO.OUT)

# def set_pin_in(pin: int):
#     GPIO.set(pin, GPIO.IN)

#we really should never need to swap a pin from input to output (do we even need inputs ever?)

def start_pwm(pin: int, freq:int = 50):
    return GPIO.PWM(pin, freq)




